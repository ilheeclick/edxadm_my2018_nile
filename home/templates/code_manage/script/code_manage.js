jQuery.ajaxSettings.traditional = true;
    $(document).ready(function() {
        setDataTable1();

    });
    function setDataTable1() {
        var $table = $('#datatable1');
        $table.dataTable({
            dom: '<"toolbar"><"search"B>rt<"bottom"ip><"clear">',
            "autoWidth": false,
            scrollX:true,
            bProcessing: true,
            ordering: false,
            serverSide: false,
            searching: true,
            "language": {
              "emptyTable": "조회된 데이터가 없습니다."
            },
            "scrollY": "250px",
            "scrollCollapse": true,
            ajax: {
                url: "/manage/group_code",
                type: "GET",
                dataType: "json",
                data: buildSearchData1,
                dataSrc: function (json) {
                    return json.data;
                }
            },
            columns: [
                {data: "pk", name: "pk"},
                {data: "group_code"},
                {data: "group_name"},
                {data: "group_desc"},
                {data: "use_yn"},
                {data: "regist_date"},
            ],
            columnDefs: [
                {
                    targets: 0, visible: true, name: "pk", render: function (data, type) {
                    return '<input type="checkbox" name="' + data + '" value="' + data + '">';
                },
                },
                {
                    targets: 1, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '"disabled>';
                },
                },
                    {
                    targets: 2, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
                    {
                    targets: 3, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
                {
                    targets: 4, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },

            ],
            rowsGroup: [
                0,
                5
            ],
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: 'Excel',
                    exportOptions: {
                    columns: [1,2,3,4,5]
                    },
                    filename: $("#pagetitle").text() + '-그룹코드 관리',
                }
            ],
            paginate: false,
            "info":false,
            initComplete: fnInitComplete1

        })
        ;

        $table.on('click','tr',function(){
			group_code = $(this).find("input[type='text']").val();
            update2();
		});
    };
    var flag = 0;
    var fnInitComplete1 = function(){
        $('.buttons-html5').attr('class', 'btn btn-primary');
        $('.form-control').change(function() {
            $(this).parent().parent().find('input:checkbox').prop("checked", true);
        });
        if(flag == 0 ) {
            setDataTable2();
            flag += 1;
        }
    }


    function buildSearchData1() {
        var obj = {
            csrfmiddlewaretoken: '{{ csrf_token }}',
        }
        return obj
    }

    function setDataTable2() {
        var $table = $('#datatable2');

        $table.dataTable({
            dom: '<"toolbar"><"search"B>rt<"bottom"ip><"clear">',
            bProcessing: true,
            ordering: false,
            serverSide: false,
            searching: true,
            "language": {
              "emptyTable": "조회된 데이터가 없습니다."
            },
            "scrollY": "250px",
            "scrollCollapse": true,
            ajax: {
                url: "/manage/detail_code",
                type: "GET",
                dataType: "json",
                data: buildSearchData2,
                dataSrc: function (json) {
                    return json.data;
                }
            },
            columns: [
                {data: "pk", name: "pk"},
                {data: "group_code"},
                {data: "detail_code"},
                {data: "detail_name"},
                {data: "detail_Ename"},
                {data: "detail_desc"},
                {data: "order_no"},
                {data: "use_yn"},
                {data: "regist_date"},
            ],
            columnDefs: [
                {
                    targets: 0, visible: true, name: "pk", render: function (data, type) {
                    return '<input type="checkbox" name="' + data + '" value="' + data + '">';
                },
                },
                {targets: 1, visible: false},
                {
                    targets: 2, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
                {
                    targets: 3, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
                {
                    targets: 4, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
                {
                    targets: 5, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
                {
                    targets: 6, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
                {
                    targets: 7, visible: true, render: function (data, type) {
                    return '<p style="display:none">'+data+'</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
                },
                },
            ],
            rowsGroup: [
                0,
                5
            ],
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: 'Excel',
                    exportOptions: {
                    columns: [2,3,4,5,6,7,8]
                    },
                    filename: $("#pagetitle").text() + '-상세코드 관리',
                }
            ],
            paginate: false,
            "info":false,
            initComplete: fnInitComplete2
        });
    }
    var fnInitComplete2 = function(){
        $('.buttons-html5').attr('class', 'btn btn-primary');
        $('.form-control').change(function() {
                $(this).parent().parent().find('input:checkbox').prop("checked", true);
        });
    }
    var group_code = $('.form-control').val();
    function buildSearchData2() {
        if(group_code == undefined) {
            group_code = $('.form-control').val();
        }

        var obj = {
            csrfmiddlewaretoken: '{{ csrf_token }}',
            user_id: '{{ user_id }}',
            group_code: group_code,
        }
        return obj
    }

    function checked_all1() {
            console.log($("#check_all1").is(":checked"));

            if ($("#check_all1").is(":checked")) {
                $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", true);
            } else {
                $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", false);
            }
        }

    function checked_all2() {
            console.log($("#check_all2").is(":checked"));

            if ($("#check_all2").is(":checked")) {
                $("#datatable2 tbody input[type=checkbox]:visible").prop("checked", true);
            } else {
                $("#datatable2 tbody input[type=checkbox]:visible").prop("checked", false);
            }
        }

    var cnt1 = 0;

    function add_row1() {
        if(cnt1 == 0) {
            $("#notice_body1").append("<tr>");
            $("#notice_body1").append("<td></td>");
            $("#notice_body1").append("<td><input type='test' class='form-control' id ='group_code'></td>");
            $("#notice_body1").append("<td><input type='test' class='form-control' id ='group_name'></td>");
            $("#notice_body1").append("<td><input type='test' class='form-control' id ='group_desc'></td>");
            $("#notice_body1").append("<td><input type='test' class='form-control' id ='use_yn'></td>");
            $("#notice_body1").append("<td></td>");
            $("#notice_body1").append("</tr>");
        }
        cnt1 += 1;
    }
    var cnt2 = 0;

    function add_row2() {
        if(cnt2 == 0) {
            $("#notice_body2").append("<tr>");
            $("#notice_body2").append("<td></td>");
            $("#notice_body2").append("<td><input type='test' class='form-control' id ='detail_code'></td>");
            $("#notice_body2").append("<td><input type='test' class='form-control' id ='detail_name'></td>");
            $("#notice_body2").append("<td><input type='test' class='form-control' id ='detail_Ename'></td>");
            $("#notice_body2").append("<td><input type='test' class='form-control' id ='detail_desc'></td>");
            $("#notice_body2").append("<td><input type='test' class='form-control' id ='order_no'></td>");
            $("#notice_body2").append("<td><input type='test' class='form-control' id ='use_yn'></td>");
            $("#notice_body2").append("<td></td>");
            $("#notice_body2").append("</tr>");

        }
        cnt2 += 1;
    }
    function Save1() {
        $("#notice_body1 input[type=checkbox]:checked").each(function() {
            var t = $('#datatable1').DataTable();
            $(this).prop('checked', false);
            var $row = $(this).closest('tr');
            var data = t.row($row.get(0)).data();
            var group_name = $(this).parent().next().next().find("input[type='text']").val();
            var group_desc = $(this).parent().next().next().next().find("input[type='text']").val();
            var use_yn = $(this).parent().next().next().next().next().find("input[type='text']").val();
            var group_code_prev = data.group_code;

            try {
            var method = 'update';
            $.post("/manage/group_code_db/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                group_name: group_name,
                group_desc: group_desc,
                use_yn: use_yn,
                group_code_prev: group_code_prev,
                user_id: {{ user.id }},
                method: method,
            }).done(function (data) {
                update1();
            }).fail(function (error) {
                swal("경고", "", "warning");
            });
            } catch (e) {
                alert(e);
            }
        });

        if(cnt1 == 1) {
            var group_code = $('#group_code').val();
            var group_name = $('#group_name').val();
            var group_desc = $('#group_desc').val();
            var use_yn = $('#use_yn').val();

            if( group_code == '') {
                swal("경고", "추가된 행의 공통코드 입력필수.", "warning");
            }
            else if (use_yn != 'Y' && use_yn != 'N') {
                swal("경고", "사용여부는 Y나 N만 입력가능.", "warning");
            }
            else {
                try {
                    var method = 'add_row_save';

                    $.post("/manage/group_code_db/", {
                        csrfmiddlewaretoken: $.cookie('csrftoken'),
                        group_code: group_code,
                        group_name: group_name,
                        group_desc: group_desc,
                        use_yn: use_yn,
                        user_id: {{ user.id }},
                        method: method,
                    }).done(function (data) {
                        update1();
                    }).fail(function (error) {
                        swal("경고", "공통코드 중복 불가능.", "warning");
                    });
                } catch (e) {
                    alert(e);
                }
            }
        }
    }

    function Save2() {
        $("#notice_body2 input[type=checkbox]:checked").each(function() {
            var t = $('#datatable2').DataTable();
            $(this).prop('checked', false);
            var $row = $(this).closest('tr');
            var data = t.row($row.get(0)).data();
            var detail_code = $(this).parent().next().find("input[type='text']").val();
            var detail_name = $(this).parent().next().next().find("input[type='text']").val();
            var detail_Ename = $(this).parent().next().next().next().find("input[type='text']").val();
            var detail_desc = $(this).parent().next().next().next().next().find("input[type='text']").val();
            var order_no = $(this).parent().next().next().next().next().next().find("input[type='text']").val();
            var use_yn = $(this).parent().next().next().next().next().next().next().find("input[type='text']").val();
            var group_code_prev = data.group_code;
            var detail_code_prev = data.detail_code;

            try {
            var method = 'update';
            $.post("/manage/detail_code_db/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                detail_code: detail_code,
                detail_name: detail_name,
                detail_Ename: detail_Ename,
                detail_desc: detail_desc,
                order_no: order_no,
                use_yn: use_yn,
                group_code_prev: group_code_prev,
                detail_code_prev: detail_code_prev,
                user_id: {{ user.id }},
                method: method,
            }).done(function (data) {
                update2();
            }).fail(function (error) {
                swal("경고", "", "warning");
            });
            } catch (e) {
                alert(e);
            }
        });

        if (cnt2 == 1) {
            var group_code = $('.form-control').val();
            var detail_code = $('#detail_code').val();
            var detail_name = $('#detail_name').val();
            var detail_Ename = $('#detail_Ename').val();
            var detail_desc = $('#detail_desc').val();
            var order_no = $('#order_no').val();
            var use_yn = $('#use_yn').val();

            if( detail_code == '') {
                swal("경고", "추가된 행의 상세코드 입력필수.", "warning");
            }
            else if (use_yn != 'Y' && use_yn != 'N') {
                swal("경고", "사용여부는 Y나 N만 입력가능.", "warning");
            }
            else {
                try {
                    var method = 'add_row_save';

                    $.post("/manage/detail_code_db/", {
                        csrfmiddlewaretoken: $.cookie('csrftoken'),
                        group_code: group_code,
                        detail_code: detail_code,
                        detail_name: detail_name,
                        detail_Ename: detail_Ename,
                        detail_desc: detail_desc,
                        order_no: order_no,
                        use_yn: use_yn,
                        user_id: {{ user.id }},
                        method: method,
                    }).done(function (data) {
                        update2();
                    }).fail(function (error) {
                        swal("경고", "상세코드 중복 불가능.", "warning");
                    });
                } catch (e) {
                    alert(e);
                }
            }
        }
    }
    function update1() {
        var table = $('#datatable1').DataTable();
        table.ajax.reload(fnInitComplete1);
        cnt1 = 0;
    }
    function update2() {
        var table = $('#datatable2').DataTable();
        table.ajax.reload(fnInitComplete2);
        cnt1 = 0;
    }

    function Del1() {
        var t = $('#datatable1').DataTable();
        var group_code_list = '';
        $("#notice_body1 input[type=checkbox]:checked").each(function() {
            $(this).prop('checked', false);
            var $row = $(this).closest('tr');
            var data = t.row($row.get(0)).data();
            var group_code = data.group_code;
            group_code_list += group_code + "+";
        });
        try {
            var method = 'del';

            $.post("/manage/group_code_db/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                group_code_list: group_code_list,
                user_id: {{ user.id }},
                method: method,
            }).done(function (data) {
                update1();
            }).fail(function (error) {
                swal("경고", "", "warning");
            });
        } catch (e) {
            alert(e);
        }
    }

    function Del2() {
        var t = $('#datatable2').DataTable();
        var detail_code_list = '';
        var group_code ='';
        $("#notice_body2 input[type=checkbox]:checked").each(function() {
            $(this).prop('checked', false);
            var $row = $(this).closest('tr');
            var data = t.row($row.get(0)).data();
            var detail_code = data.detail_code;
            group_code = data.group_code;
            detail_code_list += detail_code + "+";
        });
        try {
            var method = 'del';

            $.post("/manage/detail_code_db/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                detail_code_list: detail_code_list,
                group_code: group_code,
                user_id: {{ user.id }},
                method: method,
            }).done(function (data) {
                update2();
            }).fail(function (error) {
                swal("경고", "", "warning");
            });
        } catch (e) {
            alert(e);
        }

    }