$(function(){	
	$('#myfile').change(function(e){

		var file = e.target.files[0];
		var reader = new FileReader();

		var cvs = document.getElementById('cvs1');
		var ctx = cvs.getContext('2d');

		if(file.type.indexOf("image") < 0){
			return false;
		}

		reader.onload = (function(file){
			return function(e){
				var img = new Image();
				img.src = e.target.result;
				img.onload = function() {
					ctx.drawImage(img, 0, 0, 300, 300);
				}
			};
		})(file);
		reader.readAsDataURL(file);
	});
});
function callPostMethod() {
	var data = {};
	var cvs = document.getElementById('cvs1');
	var req = new XMLHttpRequest();

	req.onreadystatechange = function() {
		if (req.readyState == 4) {
			if (req.status == 200) {
				var output = document.getElementById('output');
				var blob = req.response;
				var imgSrc = URL.createObjectURL(blob);
				output.src = imgSrc;
			}
		}
	}

	req.open('POST', '/api/moneycount', true);
	req.setRequestHeader('content-type','application/json');
	req.responseType="blob"
	req.send(JSON.stringify(cvs.toDataURL('image/jpeg').split('base64,')[1]));
}