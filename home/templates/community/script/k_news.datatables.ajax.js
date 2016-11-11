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
			rowReorder: true,
			sAjaxSource: $table.data('url'),
			//sDom: "<T>"+'B<"toolbar"><"search"f>rt<"bottom"ip><"clear">',
			//sDom: 'T<"clear">lfrtip',
			"order": [[ 2, "asc" ]],
			"fnReloadAjax": true,
			"fnServerParams": function ( aoData ) {
				 aoData.push({ "name": 'method', "value": 'knews_list'});
			},


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
					"targets": [0],
					"visible": false,
					"searchable": false,
					"data":null,
					//"deferRender": true
					//"defaultContent": "<td>" +
					//"<input type='checkbox' />" +
					//"</td>"
				},
				{
					"targets": [1],
					"visible": false,
					"searchable": false,

					"data":null
				}
			],

			"paginate": true,
			"initComplete": function(settings, json){
				$('input[type="search"]').attr('placeholder', '검색하세요');
				$('input[type="search"]').attr('class', 'form-control');
				$('input[type="search"]').css('width', '200px');
				//$('#ZeroClipboard_TableToolsMovie_1').css('align','left');
				$('#ToolTables_datatable-ajax_0').attr('class', 'btn btn-default');
				$('#ToolTables_datatable-ajax_1').attr('class', 'btn btn-default');
				$("div.toolbar").html('<b>결과 내 검색</b>');
				this.api().columns().every( function (i) {

					//if (i == 0){
					//	return;
					//}

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


		$table.on('click','tr',function(){
			var $row;
			var cell;
			var data;
			var t = $('#datatable-ajax').DataTable();
			$row = $(this).closest('tr');
			cell = $(this).closest('td');
			data = t.row($row.get(0)).data();
			var noti_id = data[0];
			//alert(data[2]);
			location.href='/modi_knews/'+data[0]+'/'+data[1]
		});

	};

	$(function() {
		datatableInit();
	});

}).apply(this, [jQuery]);

