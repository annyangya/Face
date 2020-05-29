
from flask import request, Blueprint
from object_detection.utils import ops as utils_ops
import os
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import cv2
from gevent import monkey
monkey.patch_all()
import tensorflow as tf
from application import app,db
from common.models.Student import Student
from common.lib.Helper import getCurrentDate
from flask import jsonify

route_face = Blueprint("face_page", __name__)

PATH_TO_FROZEN_GRAPH = "/Users/apple/Downloads/11人脸识别/projects/flask_faceReg/Pbmodel/frozen_inference_graph.pb"
PATH_TO_LABELS = "/Users/apple/Downloads/11人脸识别/projects/flask_faceReg/object_detection/face_label_map.pbtxt"
IMAGE_SIZE = (256, 256)
detection_sess = tf.Session()
with detection_sess.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
        ops = tf.get_default_graph().get_operations()
        all_tensor_names = {output.name for op in ops for output in op.outputs}
        tensor_dict = {}
        for key in [
            'num_detections', 'detection_boxes', 'detection_scores',
            'detection_classes', 'detection_masks'
        ]:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                    tensor_name)
        if 'detection_masks' in tensor_dict:
            detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
            detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
            real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
            detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
            detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
            detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                detection_masks, detection_boxes, IMAGE_SIZE[0], IMAGE_SIZE[1])
            detection_masks_reframed = tf.cast(
                tf.greater(detection_masks_reframed, 0.5), tf.uint8)
            # Follow the convention by adding back the batch dimension
            tensor_dict['detection_masks'] = tf.expand_dims(
                detection_masks_reframed, 0)
        image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')


@route_face.route('/upload', methods=['POST', 'GET'])
def upload():
    f = request.files.get('file')
    print(f)
    upload_path = os.path.join("../tmp/"+id+"." + f.filename.split(".")[-1])
    print(upload_path)
    f.save(upload_path)
    return upload_path

@route_face.route("/face_detect")
def inference():

    im_url = request.args.get("url")

    im_data = cv2.imread(im_url)
    sp = im_data.shape
    im_data = cv2.resize(im_data, IMAGE_SIZE)
    output_dict = detection_sess.run(tensor_dict,
                                     feed_dict={image_tensor:
                                                    np.expand_dims(
                                                        im_data, 0)})

    # all outputs are float32 numpy arrays, so convert types as appropriate
    output_dict['num_detections'] = int(output_dict['num_detections'][0])
    output_dict['detection_classes'] = output_dict[
        'detection_classes'][0].astype(np.uint8)
    output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
    output_dict['detection_scores'] = output_dict['detection_scores'][0]

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0

    for i in range(len(output_dict['detection_scores'])):
        if output_dict['detection_scores'][i] > 0.1:
            bbox = output_dict['detection_boxes'][i]
            y1 = IMAGE_SIZE[0] * bbox[0]
            x1 = IMAGE_SIZE[1] * bbox[1]
            y2 = IMAGE_SIZE[0] * (bbox[2])
            x2 = IMAGE_SIZE[1] * (bbox[3]) #对应256*256size的坐标信息
            print(output_dict['detection_scores'][i], x1, y1, x2, y2)

    return str([x1, y1, x2, y2])


#######################################################
face_feature_sess = tf.Session()
ff_pb_path = "/Users/apple/Downloads/11人脸识别/projects/flask_faceReg/Pbmodel/face_recognition_model.pb"
with face_feature_sess.as_default():
    ff_od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(ff_pb_path, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

        ff_images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        ff_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

        ff_embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")


#图片标准化
def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    std_adj = np.maximum(std, 1.0/np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1/std_adj)
    return y

#图片读取函数，人脸检测之后的图片
def read_image(path):
    im_data = cv2.imread(path)
    im_data = prewhiten(im_data)
    im_data = cv2.resize(im_data, (160, 160))
    #1 * h * w * 3
    return im_data

@route_face.route('/face_register', methods=['POST', 'GET'])
def face_register():
    f = request.files.get('file')
    print(f)
    upload_path = os.path.join("./tmp/"+id+"." + f.filename.split(".")[-1])
    print(upload_path)
    f.save(upload_path)
    ##人 脸检测
    im_data = cv2.imread(upload_path)
    sp = im_data.shape
    im_data_re = cv2.resize(im_data, IMAGE_SIZE)
    output_dict = detection_sess.run(tensor_dict,
                                     feed_dict={image_tensor:
                                         np.expand_dims(
                                             im_data_re, 0)})

    output_dict['num_detections'] = int(output_dict['num_detections'][0])
    output_dict['detection_classes'] = output_dict[
        'detection_classes'][0].astype(np.uint8)
    output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
    output_dict['detection_scores'] = output_dict['detection_scores'][0]

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0

    for i in range(len(output_dict['detection_scores'])):
        if output_dict['detection_scores'][i] > 0.1:
            bbox = output_dict['detection_boxes'][i]
            y1 = bbox[0]
            x1 = bbox[1]
            y2 = (bbox[2])
            x2 = (bbox[3])
            print(output_dict['detection_scores'][i], x1, y1, x2, y2)
            y1 = int(y1 * sp[0])
            x1 = int(x1 * sp[1])
            y2 = int(y2 * sp[0])
            x2 = int(x2 * sp[1])
            face_data = im_data[y1:y2, x1:x2]
            im_data = prewhiten(face_data)
            im_data = cv2.resize(im_data, (160, 160))
            im_data1 = np.expand_dims(im_data, axis=0)
            emb1 = face_feature_sess.run(ff_embeddings,
                                         feed_dict={ff_images_placeholder: im_data1, ff_train_placeholder: False})

            strr = ",".join(str(i) for i in emb1[0])
            with open("./face/feature_"+id+".txt", "w") as f:
                f.writelines(strr)
            f.close()
            mess = "success"
            break
        else:
            mess = "fail"

    return mess

@route_face.route('/face_login', methods=['POST', 'GET'])
def face_login():
    f = request.files.get('file')
    print(f)
    upload_path = os.path.join("./tmp/login_"+id+"." + f.filename.split(".")[-1])
    print(upload_path)
    f.save(upload_path)
    im_data = cv2.imread(upload_path)
    sp = im_data.shape
    im_data_re = cv2.resize(im_data, IMAGE_SIZE)
    output_dict = detection_sess.run(tensor_dict,
                                     feed_dict={image_tensor:
                                         np.expand_dims(
                                             im_data_re, 0)})

    output_dict['num_detections'] = int(output_dict['num_detections'][0])
    output_dict['detection_classes'] = output_dict[
        'detection_classes'][0].astype(np.uint8)
    output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
    output_dict['detection_scores'] = output_dict['detection_scores'][0]

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0

    for i in range(len(output_dict['detection_scores'])):
        if output_dict['detection_scores'][i] > 0.1:
            bbox = output_dict['detection_boxes'][i]
            y1 = bbox[0]
            x1 = bbox[1]
            y2 = (bbox[2])
            x2 = (bbox[3])
            print(output_dict['detection_scores'][i], x1, y1, x2, y2)
            y1 = int(y1 * sp[0])
            x1 = int(x1 * sp[1])
            y2 = int(y2 * sp[0])
            x2 = int(x2 * sp[1])
            face_data = im_data[y1:y2, x1:x2]
            cv2.imwrite("face_"+id+".jpg",face_data )
            im_data = prewhiten(face_data)  # 预处理
            im_data = cv2.resize(im_data, (160, 160))
            im_data1 = np.expand_dims(im_data, axis=0)
            emb1 = face_feature_sess.run(ff_embeddings,
                                         feed_dict={ff_images_placeholder: im_data1, ff_train_placeholder: False})

            with open("./face/feature_"+id+".txt") as f:
                fea_str = f.readlines()
                f.close()
            emb2_str = fea_str[0].split(",")
            emb2 = []
            for ss in emb2_str:
                emb2.append(float(ss))
            emb2 = np.array(emb2)

            dist = np.linalg.norm(emb1 - emb2)
            print("dist---->", dist)

            if dist < 0.4:
                return "success"
            else:
                return "fail"
    return "fail"

@route_face.route("/upload_info",methods=['POST', 'GET'])
def upload_info():
    req = request.values
    global id
    id = req['id'] if 'id' in req else 0
    name = req['name'] if 'name' in req else ""
    app.logger.info("name:"+name+" no:"+id)
    student = Student()
    student.updated_time = getCurrentDate()
    student.no = id
    student.name = name
    student.status = 0
    db.session.add(student)
    db.session.commit()
    return ""

@route_face.route("/face_status",methods=['POST', 'GET'])
def face_status():
    req = request.values
    status = req['status'] if 'status' in req else 0
    app.logger.info('status:'+status)
    return ''


@route_face.route("/face_affirm",methods=['POST', 'GET'])
def affirm_status():
    from application import db as db2
    req = request.values
    status =req['status'] if 'status' in req else 0
    app.logger.info("status:"+status)
    app.logger.info("id:"+id)
    student = Student.query.filter_by(no=id).first()
    student.status = 1
    db.session.query(Student).filter_by(no=id).update({'status':1})
    return''

#####################################################################
import dlib
#检测器和关键点预测器
predictor = dlib.shape_predictor("/Users/apple/Downloads/11人脸识别/projects/flask_faceReg/Pbmodel/shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()

@route_face.route("/face_landmark_dlib", methods=['POST', 'GET'])
def face_landmark_dlib():
    f = request.files.get("file")
    upload_path = os.path.join("tmp/tmp_landmark."+f.filename.split(".")[-1])
    f.save(upload_path)
    print(upload_path)
    im_data = cv2.imread(upload_path)
    im_data = cv2.cvtColor(im_data, cv2.COLOR_BGR2GRAY)
    sp = im_data.shape
    recta = detector(im_data, 0)
    res = []
    for face in recta:
        shape = predictor(im_data, face)
        for pt in shape.parts():
            pt_pos = (pt.x, pt.y)
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            ptx = (pt.x - x1) * 1.0 / (x2 - x1)
            pty = (pt.y - y1) * 1.0 / (y2 - y1)

            res.append(str(ptx))
            res.append(str(pty))

            res.append(str(pt.x * 1.0 / sp[1]))
            res.append(str((pt.y * 1.0 / sp[0])))
        if res.__len__() == 136 * 2:
            res = ",".join(res)
            print(res)
            return res

    return "error"



