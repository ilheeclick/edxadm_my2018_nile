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
			dom: '<"toolbar"><"search"f>rt<"bottom"ip><"clear">',

			"columnDefs":[
				{
					//"targets": [0],
					"visible": true,
					"searchable": false,
					"ordering": false,
					"data":null,
					"deferRender": true
					//"defaultContent": "<td>dd</td>"
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

	};

	$(function() {
		datatableInit();
	});

}).apply(this, [jQuery]);

