//获取应用实例
var app = getApp();
Page({
    data: {
        no:'',
        name:'',
        isDisabled:true,
        text:"编辑",
        show_name:'',
        show_no:''
    },
    forNo(e){
        this.data.no = e.detail.value
    },
    forName(e) {
        this.data.name = e.detail.value
    },
    onLoad() {
        // var that = this;
        // var db = "no";
        // wx.getUserInfo({
        //   success:function (res) {
        //       that.data.no = res.userInfo.no,
        //       that.data.name = res.userInfo.name,
        //       that.setData({
        //         no: that.data.no,
        //         name: that.data.name,  
        //       }),
        //       that.setData({
        //           db: "ok"
        //       })
        //       if(db = "ok"){
        //           var stu_name,stu_no;
        //           wx.request({
        //             url: 'http://192.168.0.101:5000/face/upload',
        //             header: { "Content-type": "multipart/form-data" },
        //             method: "POST",
        //             data :{
        //                 stu_name: res.userInfo.name,
        //                 stu_no: res.userInfo.no,
        //             },
        //             success:function () {
        //                 console.log("success")
        //             },
        //             fail:function () {
        //                 console.log("fail")
        //             }
        //           })
        //       }
        //   },
        //   fail:function name(res) {
        //       that.data.name = "用户未知",
        //       that.setData({
        //           name: that.data.name
        //       })
        //   }
        // })
    },
    onShow() {
        let that = this;
        that.setData({
            user_info: {
                nickname: "annYangya",
                avatar_url: "/images/more/logo.png"
            },
        })
    },
    
    btn_save:function name() {
        var stu_name = this.data.name;
        var stu_no = this.data.no;
        var that = this
        console.log("stu_no:"+stu_no +" stu_name:"+stu_name)
        if(stu_name!=""&&stu_no!=""&&that.data.text=="编辑"){
            wx.request({
              url: 'http://10.137.31.232:5000/face/upload_info',
              data:{"id":that.data.no,"name":that.data.name},
              header: {'Content-Type': 'application/json'},
              success: function(res){
                      that.setData({
                          isDisabled:false,
                          text:"禁用",
                          show_no:that.data.no,
                          show_name:that.data.name
                      })
                      wx.showToast({
                        title: '保存成功！'
                      })
                  
              } 
            })
        }else{
            wx.showToast({
              title: '输入框不能为空！',
            })
        }
    }
});