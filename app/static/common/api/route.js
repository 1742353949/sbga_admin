var route = function() {
	this.url = "http://127.0.0.1:5000"
	this.prefix = this.url + "/route"
	
	// 路由设置
	this.route = {
		"login":{
			"name":"登录",
			"url":this.prefix + "/login"
		},
		"index":{
			
		},
		"de_2_line":{
			"name":"故障超两次线路",
			"url":"/static/common/json/index.json"
		},
	}
	
	return this.route;
	
}

