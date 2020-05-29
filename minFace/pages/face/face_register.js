//index.js
//获取应用实例
var time = null;
var myCanvas = null;
var windowHeight, windowWidth;
var register_img = null;
var type = null;
Page({
  data: {
    device: true,
    camera: true,
    x1: 0,
    y1: 0,
    x2: 0,
    y2: 0,
  },
  onLoad() {
    this.setData({
      ctx: wx.createCameraContext(),
      device: this.data.device,
    })
    wx.getSystemInfo({
      success: function (res) {
        console.log(res);
        windowHeight = res.windowHeight;
        windowWidth = res.windowWidth;
        console.log('height=' + res.windowHeight);
        console.log('width=' + res.windowWidth);
      }
    })
  },
  register(){
    let that = this
    //上传
    wx.uploadFile({
      url: 'http://10.137.31.232:5000/face/face_register',
      filePath: register_img,
      name: 'file',
      header: { "Content-type": "multipart/form-data" },
      success: function (res) {
        if(res.data == "success"){
          that.setData({
            register_res:"注册成功" 
          })
        }
        else{
          that.setData({
            register_res: "注册失败"
          })
        }
      },
      fail:function(res){
        that.setData({
          register_res: "注册失败"
        })
      }
    })
  },
  open() {
    this.setData({
      camera: true
    })
    type = "takePhoto";
    let ctx = wx.createCameraContext(this)
    let that = this
      if (type == "takePhoto") {
        console.log("开始拍照")
        ctx.takePhoto({
          quality: "normal",
          success: (res) => {
            console.log(res.tempImagePath)
            var tempImagePath = res.tempImagePath
            register_img = tempImagePath
            wx.uploadFile({
              url: 'http://10.137.31.232:5000/face/upload',
              filePath: tempImagePath,
              name: 'file',
              header: { "Content-type": "multipart/form-data" },
              success: function (res) {
                var im_path = res.data
                console.log(im_path)
              }
            })
          }
        })
      }
  },
  // 关闭模拟的相机界面
  close() {
    console.log("关闭相机");
    type = "endPhoto"
  },
})
//人脸匹配，相似度，欧式距离