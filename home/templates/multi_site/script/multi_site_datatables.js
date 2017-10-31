/*
Name: 			Tables / Ajax - Examples
Written by: 	Okler Themes - (http://www.okler.net)
Theme Version: 	1.5.2
*/

(function($) {

	'use strict';
	var datatableInit = function() {

		var $table = $('#datatable33');

		$table.dataTable({
			bProcessing: true,
			rowReorder: true,
			sAjaxSource: $table.data('url'),
			//sDom: "<T>"+'B<"toolbar"><"search"f>rt<"bottom"ip><"clear">',
			//sDom: 'T<"clear">lfrtip',
			"order": [[ 0, "desc" ]],
			"fnReloadAjax": true,
			"fnServerParams": function ( data ) {
				 data.push({ "name": 'method', "value": 'multi_site_list'});
			},


			dom: '<"toolbar"><"search"f>rt<"bottom"ip><"clear">',

			"paginate": true,
			"columnDefs":[
				{
					"targets": [1],
					"visible": false,
				},
				{targets: 0, visible: true, width: '6%'},
				{targets: 7, visible: true, width: '8%'},

			],

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
			var t = $('#datatable33').DataTable();
			$row = $(this).closest('tr');
			data = t.row($row.get(0)).data();
			location.href='/manage/modi_multi_site/'+data[1]
		});
	};


	$(function() {
		datatableInit();
	});

}).apply(this, [jQuery]);

