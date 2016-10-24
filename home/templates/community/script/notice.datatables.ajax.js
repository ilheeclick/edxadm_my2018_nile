/*
Name: 			Tables / Ajax - Examples
Written by: 	Okler Themes - (http://www.okler.net)
Theme Version: 	1.5.2
*/

(function($) {
	//'use strict';
    //
	//$('#sel_assess').select2({placeholder: '평가를 선택하세요'});*
	var datatableInit = function() {

		var $table = $('#datatable-ajax');


		$table.dataTable({
			bProcessing: true,
			"bFilter": false,
			sAjaxSource: $table.data('url'),
			//dom: 'Bfrtip',
			"columnDefs":[
				{
					"targets": [0],
					"visible": true,
					"searchable": false,
					"orderable": false,
				},

			],
			"paginate": true,
		});
	};

	//$('#add_notice').on('click',function(){
	//	$('#modal').modal('show');
	//});
    //
	//$('#notice_save').on('click', function(e){
	//		try{
	//			var action_mode;
	//			var noticetitle, noticecontent;
	//			var value_list;
	//			var html;
	//			noticetitle = $('#noticetitle').val();
	//			noticecontent = $('.summernote').summernote('code');
	//			//alert(noticetitle + ' / '  + noticecontent);
	//			action_mode = 'add';
    //
	//			/* insert to database */
	//			$.post("/save_notice/", {
	//				csrfmiddlewaretoken:$.cookie('csrftoken'),
	//				nt_title: noticetitle,
	//				nt_cont: noticecontent,
	//				method: action_mode
	//			}).done(function(data){
	//				//value_list = data[0].toString().split(',');
	//				//console.log(value_list)
	//				console.log(data)
	//				html='<tr>' +
	//						'<td><input type="checkbox"> 1</td>'+
	//						'<td>'+data[0]+'</td>'+
	//						'<td>'+data[2].substring(0,10)+'</td>'+
	//						'<td>'+data[3]+'</td>'+'</tr>'
	//				$('#notice_body').append(html);
	//				$('#modal').modal('hide');
	//			}).fail(function(error) {
	//				alert('error = ' + error.responseJSON);
	//			});
    //
	//		}catch(e){
	//			alert(e);
	//		}
	//});
    //
	//$('#del_notice').on('click', function(){
	//	var del_sel=$('#del_sel').val();
	//	if(del_sel=='전체 삭제'){
	//		alert('전체삭제 하실래예?');
	//	}
	//});

		//$('#summernote').summernote({
		//	onblur : function(e){
		//		$('#summercontent').html($('$summernote').code());
		//	},
		//	height : 4000,
		//	minHeight : 200,
		//	maxHeight : null,
		//	lang : 'ko-KR'
		//});


	$(function() {
		datatableInit();

	});

}).apply(this, [jQuery]);

