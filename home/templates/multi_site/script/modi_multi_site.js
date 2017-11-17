jQuery.ajaxSettings.traditional = true;
    $(document).ready(function(){
        setDataTable1();
        var value_list;
        var id = '{{id}}';
        if (id != 99999) {

            document.getElementById('DelBtn').style.display = '';
            document.getElementById('row_DelBtn').style.display = '';
            document.getElementById('row_SaveBtn').style.display = '';
            document.getElementById('add_row_DelBtn').style.display = 'none';
            document.getElementById('add_row_SaveBtn').style.display = 'none';


        }
           $.ajax({
                url: '/manage/modi_multi_site/' + id,
                data: {
                    method: 'modi'
                }
            }).done(function (data) {
               if(data != '') {
                   value_list = data[0].toString().split(',');
                   $('#site_name').val(data[0][0]);
                   $('#site_code').val(data[0][1]);
                   $('#site_url').val(data[0][2]);
               }
            })
    });

    function save() {
        var uploadfile = $('#uploadfile').val();
        var site_name = $('#site_name').val();
        var site_code = $('#site_code').val();
        var site_url = $('#site_url').val();


        if(site_name == '') {
            swal("경고", "기관명 입력해주세요.", "warning");
        }
        else if(site_code == '') {
            swal("경고", "기관코드를 입력해주세요.", "warning");
        }
        else if(uploadfile == '') {
            swal("경고", "기관이미지를 선택해주세요.", "warning");
        }
        else if(site_url == '') {
            swal("경고", "접속 url을 입력해주세요.", "warning");
        }
        else {
            document.getElementById("uploadform").submit();

            try {
                var method = '';
                var site_index = '';
                if ('{{ id }}' == 99999) {
                    method = 'add';
                }
                else {
                    method = 'modi';
                }
                var site_name = $('#site_name').val();
                var site_code = $('#site_code').val();
                var site_url = $('#site_url').val();
                var regist_id = '{{ user.id }}';
                var multi_no = '{{ id }}';
                var email_list = "";
                $(".email").each(function () {
                    if ($(this).text() != '') {
                        email_list += $(this).text() + "+";
                    }
                });

                $.post("/manage/modi_multi_site_db/", {
                    csrfmiddlewaretoken: $.cookie('csrftoken'),
                    site_name: site_name,
                    site_code: site_code,
                    site_url: site_url,
                    regist_id: regist_id,
                    multi_no: multi_no,
                    site_index: site_index,
                    email_list: email_list,
                    method: method,
                }).done(function (data) {
                    location.href = '/manage/multi_site';
                }).fail(function (error) {
                    alert('errorasdfasf = ' + error.responseJSON);
                });
            } catch (e) {
                alert(e);
            }
        }
    }

    function del() {
        try {
            var multi_no = '{{ id }}';
            $.post("/manage/modi_multi_site_db/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                multi_no: multi_no,
                method: 'delete',
            }).done(function (data) {
                location.href = '/manage/multi_site';
            }).fail(function (error) {
                alert('error = ' + error.responseJSON);
            });
        } catch (e) {
            alert(e);
        }
    }

    function setDataTable1() {
        var $table = $('#datatable1');

        $table.dataTable({
            dom: '<"clear">lfrtip',
            bProcessing: true,
            ordering: false,
            serverSide: false,
            searching: false,
            "language": {
              "emptyTable": " "
            },
            buttons: [
                {
                    text: 'Row selected data',
                    action: function (e, dt, node, config) {
                        alert(
                                'Row data: ' +
                                JSON.stringify(dt.row({selected: true}).data())
                        );
                    },
                    enabled: false
                }
            ],
            ajax: {
                url: "/manage/manager_list",
                type: "GET",
                dataType: "json",
                data: buildSearchData1,
                dataSrc: function (json) {
                    return json.data;
                }
            },
            columns: [
                {data: "pk", name: "pk"},
                {data: "email", name: "email"},
                {data: "name"},
                {data: "username"},
            ],
            columnDefs: [
                {
                    targets: 0, visible: true, name: "pk", render: function (data, type) {
                    return '<input type="checkbox" name="' + data + '" value="' + data + '">';
                }, width:'8%'
                },
                {targets: 1, visible: true},
                {targets: 2, visible: true, width: '20%'},
                {targets: 3, visible: true, width: '20%'},
            ],
            rowsGroup: [
                0,
                5
            ],
            paginate: false,
            initComplete: function () {

            }
        })
        ;

    }

    function buildSearchData1() {
        var id = '{{id}}';
        var obj = {
            csrfmiddlewaretoken: '{{ csrf_token }}',
            id: id,
        }
        return obj
    }

    function checked_all() {
        console.log($("#check_all").is(":checked"));

        if ($("#check_all").is(":checked")) {
            $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", true);
        } else {
            $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", false);
        }
    }

    function del_row() {
        $("#notice_body input[type=checkbox]:checked").each(function(){
            var user_id = $(this).parent().next().next().next().text();
            var regist_id = '{{ user.id }}';
            try {
                var method = 'delete';
                $.post("/manage/manager_db/", {
                    csrfmiddlewaretoken: $.cookie('csrftoken'),
                    user_id: user_id,
                    site_id: '{{ id }}',
                    regist_id:regist_id,
                    method: method,
                }).done(function (data) {
                    update();
                    cnt = 0;
                }).fail(function (error) {
                    alert('error = ' + error.responseJSON);
                });
            } catch (e) {
                alert(e);
            }
        });
    }

    function new_del_row() {
        $("#notice_body input[type=checkbox]:checked").each(function(){
            $(this).parent().parent().css("display","none");
            alert($(this).parent().next().text());
            $(this).parent().next().html('');
            alert($(this).parent().next().text());
        });
    }

    var cnt = 0;
    var up_date = 0;

    function add_row() {
        if(cnt == 0) {
            var tr_html = $("#notice_body tr:eq(0)").html();
            $("#notice_body").append("<tr>");
            $("#notice_body").append("<td></td>");
            $("#notice_body").append("<td><div class='col-sm-15'><input type='test' class='form-control' style='width:100%' id='input_email'></div></td>");
            $("#notice_body").append("<td><a href='javascript:verify();'><input class='btn btn-default' type='button' style='width:100%' id='VeriBtn' value='검     증'></a></td>");
            $("#notice_body").append("<td><a href='javascript:save_info();'><input class='btn btn-default' type='button' style='width:100%' id='Save_Btn' value='저     장'></a></td>");
            $("#notice_body").append("</tr>");
            $('#Save_Btn').attr('disabled','disabled');
        }
        cnt = cnt + 1;
    }

    function new_add_row() {
        if(cnt == 0) {
            var tr_html = $("#notice_body tr:eq(0)").html();
            $("#notice_body").append("<tr>");
            $("#notice_body").append("<td></td>");
            $("#notice_body").append("<td><div class='col-sm-15'><input type='text' class='form-control' style='width:100%' id='input_email'></div></td>");
            $("#notice_body").append("<td><a href='javascript:verify();'><input class='btn btn-default' type='button' style='width:100%' id='VeriBtn' value='검     증'></a></td>");
            $("#notice_body").append("<td><a href='javascript:new_save_info();'><input class='btn btn-default' type='button' style='width:100%' id='Save_Btn' value='저     장'></a></td>");
            $("#notice_body").append("</tr>");
            $('#Save_Btn').attr('disabled','disabled');
        }
        cnt = cnt + 1;
    }

    var cntt = 0;
    var is_verify = 0;


    function verify() {

        var input_email = $('#input_email').val();
        try {
            var method = 'verify';
            var input_email = $('#input_email').val();

            $.post("/manage/manager_db/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                input_email: input_email,
                method: method,
            }).done(function (data) {
                if (data == 0) {
                    is_verify = 0;
                    swal("경고", "정확한 Email 을 입력하세요.", "warning");
                    $("#input_email").val('');
                }
                else if (data == 1) {
                    is_verify = 1;
                    $('#Save_Btn').removeAttr('disabled');
                    swal("성공", "정확한 Email 입니다.", "success");
                }
            }).fail(function (error) {
                alert('error = ' + error.responseJSON);
            });
        } catch (e) {
            alert(e);
        }
        cntt = cntt + 1;
    }

    function save_info() {
        if( cntt == 0 || is_verify == 0) {
            swal("경고", "정확한 Email 을 입력하세요.", "warning");
        }
        else {
            try {
                var method = 'add';
                var id = '{{id}}';
                var input_email = $('#input_email').val();
                var regist_id = '{{ user.id }}';

                $.post("/manage/manager_db/", {
                    csrfmiddlewaretoken: $.cookie('csrftoken'),
                    id: id,
                    input_email: input_email,
                    regist_id: regist_id,
                    method: method,
                }).done(function (data) {
                    update();
                    cnt = 0;
                }).fail(function (error) {
                    swal("경고", "입력한 Email 이 이미 존재합니다", "warning");
                });
            } catch (e) {
                alert(e);
            }
        }
    }

    function new_save_info() {
        $('#Save_Btn').attr('disabled','disabled');
        if( cntt == 0 || is_verify == 0) {
            swal("경고", "정확한 Email 을 입력하세요.", "warning");
        }
        else {
            try {
                var method = 'temporary';
                var input_email = $('#input_email').val();

                $.post("/manage/manager_db/", {
                    csrfmiddlewaretoken: $.cookie('csrftoken'),
                    input_email: input_email,
                    method: method,
                }).done(function (data) {
                    var flag = 0;
                    $(".email").each(function(){
                        if($(this).text() == input_email) {
                            swal("경고", "입력한 Email 이 이미 존재합니다", "warning");
                            $("#input_email").val('');
                            flag = 1;
                        }
                    });
                    if(flag == 0) {
                            $("#notice_body").prepend("<tr role='row' class='odd'><td><input type='checkbox' name='undefined' value='undefined'></td><td class = 'email'>" + data[0][0] + "</td><td>" + data[0][1] + "</td><td>" + data[0][2] + "</td></tr>");
                            $("#input_email").val('');
                        }
                    if($(".email").text() == ""){
                        $("#notice_body").prepend("<tr role='row' class='odd'><td><input type='checkbox' name='undefined' value='undefined'></td><td class = 'email'>" + data[0][0] + "</td><td>" + data[0][1] + "</td><td>" + data[0][2] + "</td></tr>");
                        $("#input_email").val('');
                    }
                    flag = 0;
                }).fail(function (error) {
                    alert('error = ' + error.responseJSON);
                });
            } catch (e) {
                alert(e);
            }
        }
    }

    function update() {
        var table = $('#datatable1').DataTable();
        table.ajax.reload();
        up_date = up_date + 1;
    }

    $(function(){
        $('#btn-upload').click(function(e){
            e.preventDefault();
            $("input:file").click();
            var ext = $("input:file").val().split(".").pop().toLowerCase();
            if(ext.length > 0){
                if($.inArray(ext, ["gif","png","jpg","jpeg"]) == -1) {
                    alert("gif,png,jpg 파일만 업로드 할수 있습니다.");
                    return false;
                }
            }
            $("input:file").val().toLowerCase();
        });
    });


