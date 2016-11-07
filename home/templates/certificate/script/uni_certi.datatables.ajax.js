/*
Name: 			Tables / Ajax - Examples
Written by: 	Okler Themes - (http://www.okler.net)
Theme Version: 	1.5.2
*/

(function($) {

	'use strict';

	var datatableInit = function() {

		var $table = $('#datatable-ajax');
		$table.dataTable({
			bProcessing: true,
			sAjaxSource: $table.data('url'),

			dom: 'T<"clear"><"toolbar"><"search"f>rt<"bottom"ip><"clear">',
			oTableTools: {
				sSwfPath: $table.data('swf-path'),
				aButtons: [
					{
						sExtends: 'xls',
						sButtonText: 'Excel'
					},
					{
						sExtends: 'print',
						sButtonText: 'Print',
						sInfo: 'Please press CTR+P to print or ESC to quit'
					}
				]
			},

			"columnDefs":[
				{
					"targets": -1,
					//"visible": true,
					//"searchable": false,
					//"ordering": false,
					"data":null,
					//"deferRender": true,
					"defaultContent": "<td>" +
					"<input class='btn btn-primary btn-sm' id='create_certi' type='button' value='이수증 생성'></input>" +
					"</td>"
				}

		],

			"paginate": true,
			"initComplete": function(settings, json){
				$('input[type="search"]').attr('placeholder', '검색하세요');
				$('input[type="search"]').attr('class', 'form-control');
				$('input[type="search"]').css('width', '200px');
				$('#ToolTables_datatable-ajax_0').attr('class', 'btn btn-default');
				$('#ToolTables_datatable-ajax_1').attr('class', 'btn btn-default');
				$("div.toolbar").html('<b>결과 내 검색</b>');
				this.api().columns().every( function (i) {

					if (i == 0){
						return;
					}

					var column = this;
					var select = $('<select style="width: 100%;"><option value=""></option></select>')
						.appendTo( $(column.footer()).empty()).select2({placeholder: '검색필터', allowClear: true}).attr('width', '100%')
						.on( 'change', function () {
							var val = $.fn.dataTable.util.escapeRegex(
								$(this).val()
							);

							column
								.search( val ? '^'+val+'$' : '', true, false )
								.draw();
						} );

					column.data().unique().sort().each( function ( d, j ) {
						select.append( '<option value="'+d+'">'+d+'</option>' )
					} );
				} );
			}
		});
		$(document).on('click', '#uni_search', function(){
			var value_list = [];
			var html ="";
			var org = $('#org').find('option:selected').val();
			var course= $('#course').find('option:selected').val();
			var org_id = $('#org').find('option:selected').attr('id');
			var run= $('#course').find('option:selected').attr('name');
			var course_id= $('#course').find('option:selected').attr('id');
			var t = $('#datatable-ajax').DataTable();
			if(org_id == null){
				$.ajax({
					url : '/certificate/',
					data : {
						method : 'uni_certi'
					}
				}).done(function(data){
					//console.log(data);
					t.clear();
					for(var i=0; i<data.length; i++){
						//console.log(data[i][1]);
						t.row.add(data[i]).draw(true);
					}
				});
			}else if(org_id != null && course_id != null){
				$.ajax({
					url : '/certificate/',
					data : {
						method : 'uni_certi',
						org_id : org_id,
						run : run
					}
				}).done(function(data){
					//console.log(data);
					t.clear();
					if(data.length == null || data == ''){
						alert('정보가 없습니다.')
					}else{
						for(var i=0; i<data.length; i++){
							t.row.add(data[i]).draw(true);
						}
					}
				});
			}else{
				$.ajax({
					url : '/certificate/',
					data : {
						method : 'uni_certi',
						org_id : org_id
						//course_id : course_id,
					}
				}).done(function(data){
					//console.log(data);8
					t.clear();
					if(data.length == null || data == ''){
						alert('정보가 없습니다.')
					}else{
						for(var i=0; i<data.length; i++){
							t.row.add(data[i]).draw(true);
						}
					}
				});
			}
		});

		$(document).on('click', '#create_certi', function(){
			var $row;
			var data;
			var t = $('#datatable-ajax').DataTable();
			$row = $(this).closest('tr');
			data = t.row($row.get(0)).data();
			//console.log(data[0]+'/'+data[2]);
			$.ajax({
				url : '/certificate',
				data : {
					method : 'create_certi',
					org_name : data[0],
					run : data[2]
				}
			}).done(function(data){
				if(data == 'Success'){
					alert('이수증이 생성되었습니다.');
				}else{
					alert('오류가 발생했습니다.');
				}
			});
		});

	};

	$(function() {
		datatableInit();
	});

}).apply(this, [jQuery]);

