document.write('<script type="text/javascript" src="/static/common/api/route.js"></script>');
var $api = function() {
	this.url = "http://127.0.0.1:5000";
	this.route = new route();
	//get 提交
	this.get = function(url, callback, data = "") {
		console.log("api->get:" + url)
		$.ajax({
			type: 'GET',
			url: url,
			data: data,
			dataType: "json",
			success: function(res) {
				callback(res)
			},
			error: function(res) {
				console.log("请求错误！")
			}
		});
	}
	
	//获取json文件
	this.getJson = function(url,callback) {
		console.log("api->getJson:" + url)
		$.ajax({
			type: 'GET',
			url: url,
			data: "",
			dataType: "json",
			success: function(res){
				callback(res)
			},
			error: function(res) {
				console.log("请求错误！")
			}
		});
	}

	//重定向
	this.redirect = function(url) {
		console.log("api->redirect:"+url)
		return location.href = url
	}

	//获取页面传参	
	this.request = function(url, paras) {
		console.log("api->request:"+url)
		var paraString = url.substring(url.indexOf("?") + 1, url.length).split("&");
		var paraObj = {}
		for (i = 0; j = paraString[i]; i++) {
			paraObj[j.substring(0, j.indexOf("=")).toLowerCase()] = j.substring(j.indexOf("=") + 1, j.length);
		}
		var returnValue = paraObj[paras.toLowerCase()];
		// if (typeof(returnValue) == "undefined") {
		// 	location.href = "/login.html"
		// 	return false
		// } else {
			return returnValue;
		// }
		return returnValue;
	}
	
	//随机数
	this.random = function(max,min){
		return Math.floor(Math.random()*(max-min+1)+min) + (Math.floor(Math.random()*10) * 0.1) + (Math.floor(Math.random()*10) * 0.01) -1; 
	}
}
