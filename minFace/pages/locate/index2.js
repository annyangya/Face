
var amapFile = require('../../libs/amap-wx.js');
var markersData = {
 latitude: '',//纬度
 longitude: '',//经度
 key: "8b51e7d5f7b6aa22ae54a1c31ccbed32"//申请的高德地图key
};
Page({

 /**
  * 页面的初始数据
  */
 data: {
  weather:[],
 },

 /**
  * 生命周期函数--监听页面加载
  */
 onLoad: function (options) {
  this.loadInfo();
 },
 //获取当前位置的经纬度
 loadInfo: function(){
  var that=this;
  wx.getLocation({
   type: 'gcj02', //返回可以用于wx.openLocation的经纬度
   success: function (res) {
    var latitude = res.latitude//维度
    var longitude = res.longitude//经度
    console.log(res);
    that.loadCity(latitude,longitude);
   }
  })
 },

 //把当前位置的经纬度传给高德地图，调用高德API获取当前地理位置，天气情况等信息
 loadCity: function (latitude, longitude){
  var that=this;
  var myAmapFun = new amapFile.AMapWX({ key: markersData.key });
  myAmapFun.getRegeo({
   location: '' + longitude + ',' + latitude + '',//location的格式为'经度,纬度'
   success: function (data) {
    console.log(data);
   },
   fail: function (info) { }
  });

  myAmapFun.getWeather({
   success: function (data) {
    that.setData({
     weather: data
    })
    console.log(data);
    //成功回调
   },
   fail: function (info) {
    //失败回调
    console.log(info)
   }
  })
 },
})



