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
			dom: 'B<"toolbar"><"search"f>rt<"bottom"ip><"clear">',

			"columnDefs":[
				{
					"targets": -1,
					//"visible": true,
					//"searchable": false,
					//"ordering": false,
					"data":null,
					//"deferRender": true,
					"defaultContent": "<input>ddd</input>"
				}

		],

			"paginate": true,
			"initComplete": function(settings, json){
				$('input[type="search"]').attr('placeholder', '검색하세요');
				$('input[type="search"]').attr('class', 'form-control');
				$('input[type="search"]').css('width', '200px');

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


		$(document).on('click', '#per_search', function(e){
			var value_list=[];
			var org = $('#org').find('option:selected').val();
			var org_id = $('#org').find('option:selected').attr('id');
			var course= $('#course').find('option:selected').val();
			var run= $('#course').find('option:selected').attr('name');
			var course_id= $('#course').find('option:selected').attr('id');
			var html="";
			var t = $('#datatable-ajax').DataTable();
			//alert(org_id+' / '+course_id+' / '+run);
			if($('#email').val() != '' && $('#email').val().length > 4 && $('#org').find('option:selected').attr('id') != null && $('#course').find('option:selected').attr('id') != null){
				var email = $('#email').val();

				$.ajax({
					url : '/per_certificate/',
					data : {
						method : 'email_search',
						org_id : org_id,
						run : run,
						email : email
					}
				}).done(function(data){
					t.clear();
					if(data.length != 0){
						for(var i=0;i<data.length;i++){
							t.row.add(data[i]).draw(true);
						}
					}else{
						alert('정보가 없습니다.');
					}

				})
			}
			else if($('#email').val() != '' && $('#email').val().length > 4 && $('#org').find('option:selected').attr('id') == null){
				var email = $('#email').val();

				$.ajax({
					url : '/per_certificate/',
					data : {
						method : 'email_search',
						email : email
					}
				}).done(function(data){
					t.clear();
					if(data.length != 0){
						for(var i=0;i<data.length;i++){
							console.log(data[i])
							t.row.add(data[i]).draw(true);
						}
					}else{
						alert('정보가 없습니다.');
					}

				})
			}

			else if($('#org').find('option:selected').attr('id') != null && $('#course').find('option:selected').attr('id') != null ){
				var html2="";

				$.ajax({
					url : '/per_certificate/',
					data : {
						method : 'per_certi',
						org_id : org_id,
						run : run
					}
				}).done(function(data){

					t.clear();
					if(data.length == 0 || data == null){
						alert('정보가 없습니다.')
					}else{
						for(var i=0;i<data.length;i++){
							t.row.add(data[i]).draw(true);
						}
					}
				});
			}
			else if($('#email').val().length > 4 && $('#org').find('option:selected').attr('id') != null && $('#course').find('option:selected').attr('id') == null){
				alert('강좌명을 선택하세요.');
			}
			else if($('#email').val().length < 5){
				alert('검색어를 5자 이상 입력하거나 강좌를 선택하세요.');
			}

			else{
				alert('error');
			}
		})
	};

	$(function() {
		datatableInit();
	});

}).apply(this, [jQuery]);

