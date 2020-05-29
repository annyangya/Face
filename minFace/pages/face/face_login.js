//index.js
//获取应用实例
var time = null;
var myCanvas = null;
var windowHeight, windowWidth;
var type = null;
Page({
  data: {
    device: true,
    camera: true,
    x1: 0,
    y1: 0,
    x2: 0,
    y2: 0,
    status:0,
    mouth_status_1:0,
    mouth_status_2:0,
    login_info:false
  },
  onLoad() {
    this.setData({
      ctx: wx.createCameraContext(),
      device: this.data.device,
    })
    wx.getSystemInfo({
      success: function (res) {
        console.log(res);
        // 屏幕宽度、高度
        windowHeight = res.windowHeight;
        windowWidth = res.windowWidth;
        console.log('height=' + res.windowHeight);
        console.log('width=' + res.windowWidth);
      }
    })
  },
  open() {
    this.setData({
      camera: true,
      login_res:"正在登录"
    })
    type = "takePhoto";
    let ctx = wx.createCameraContext(this)
    let that = this
    time = setInterval(function () {
      if (type == "takePhoto") {
        console.log("begin takephoto")
        ctx.takePhoto({
          quality: "normal",
          success: (res) => {
            console.log(res.tempImagePath)
            var tempImagePath = res.tempImagePath
            wx.uploadFile({
              url: 'http://10.137.31.232:5000/face/face_login',
              filePath: tempImagePath,
              name: 'file',
              header: { "Content-type": "multipart/form-data" },
              success: function (res) {
                if (res.data == "success") {
                  type = "endPhoto"
                  that.setData({
                    login_res: "登录成功",
                    status:1,
                    login_info:true
                  })
                }else{
                  that.setData({
                    login_res: "登录失败"
                  })
                }
              },
              fail:function(res){
                  that.setData({
                    login_res:"登录失败"
                  })
              }  
            }) 
          }
        })
      }
    }, 500)
  },
  affirm:function name() {
    this.setData({
      camera: true
    })
    type = "takePhoto";
    let ctx = wx.createCameraContext(this)
    let that = this
    time = setInterval(function () {
      if (type == "takePhoto") {
        console.log("begin takephoto")
        ctx.takePhoto({
          quality: "normal",
          success: (res) => {
            console.log(res.tempImagePath)
            var tempImagePath = res.tempImagePath
            wx.uploadFile({
              url: 'http://10.137.31.232:5000/face/face_landmark_dlib',
              filePath: tempImagePath,
              name: 'file',
              header: { "Content-type": "multipart/form-data" },
              success: function (res) {
                if (res.data == "error") {
                }else{
                  console.log(res.data)
                  var pos = res.data.split(",")
                  myCanvas = wx.createCanvasContext('myCanvas')
                  myCanvas.drawImage(tempImagePath,0,0,windowWidth,windowHeight * 0.6)
                  myCanvas.setLineWidth(5)
                  myCanvas.setStrokeStyle("green")
                for (var i=0;i<136*2;){
                    var x = parseInt(pos[i+2] * windowWidth)
                    var y = parseInt(pos[i+3] * windowHeight * 0.6)
                    myCanvas.moveTo(x,y)
                    myCanvas.lineTo(x+1, y+1)
                    i+=4
                }
                var diff1 = pos[67 * 4 + 1]  - pos[63 * 4 + 1]
                var diff2 = pos[41 * 4 + 1] - pos[37 * 4 + 1]
                var diff3 = pos[46 * 4 + 1] - pos[44 * 4 + 1]
                console.log(diff1, diff2, diff3)
                if (diff2 < 0.03 && diff3 < 0.03){
                  that.setData({
                    eye_flag:"闭眼",
                    
                  })
                }else{
                  that.setData({
                    eye_flag:"睁眼",
                    
                  })
                }
                if (diff1 > 0.03){
                  that.setData({
                    mouth_flag:"张嘴",
                    mouth_status_1:1
                  })
                }else{
                  that.setData({
                    mouth_flag:"闭嘴",
                    mouth_status_2:1,
                  })
                }
                myCanvas.stroke()
                myCanvas.draw()
             }
              },
            }) 
          }
        })
      }
    }, 500)
  },
  status:function name(){
    var status = this.data.status
    var mouth_status_1 = this.data.mouth_status_1
    var mouth_status_2 = this.data.mouth_status_2
    var that = this
    console.log("status:"+status)
    if(mouth_status_1&&mouth_status_2){
      wx.request({
        url: 'http://10.137.31.232:5000/face/face_affirm',
        data:{"status":1},
        header: {'Content-Type': 'application/json'},
        success: function(res){
          wx.showToast({
            title: '确认成功！'
          })    
  },
      })
    }else{
      wx.showToast({
        title: '请重新登录！',
      })
    }
  },
  close() {
    console.log("关闭相机");
    type = "endPhoto"
    console.log(this.data.status)
  },
})
//图片上传，人脸检测，特征提取，相似度测量（人脸识别）