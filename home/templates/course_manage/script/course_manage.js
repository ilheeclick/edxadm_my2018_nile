jQuery.ajaxSettings.traditional = true;
$(document).ready(function () {
    setDataTable1();
});

function setDataTable1() {
    var $table = $('#datatable1');

    $table.dataTable({
        "scrollY": "400px",
        "scrollX": "4000px",
        bProcessing: true,
        rowReorder: true,
        "searching": false,
        sAjaxSource: $table.data('url'),
        "fnReloadAjax": true,
        "paging": false,
        "fnServerParams": function (data) {
            var choice = document.getElementById("choice");
            data.push({"name": 'method', "value": 'course_list'});
            data.push({"name": 'start', "value": $('#datepicker1').val()});
            data.push({"name": 'end', "value": $('#datepicker2').val()});
            data.push({"name": 'course_name', "value": $('#course_name').val()});
            data.push({"name": 'choice', "value": choice.options[choice.selectedIndex].value});
        },


        dom: '<"toolbar"><"search"B>rt<"bottom"ip><"clear">',

        "paginate": false,
        "columnDefs": [
            {
                targets: 0, visible: true, name: "pk", render: function (data, type) {
                return '<input type="checkbox" name="' + undefined + '" value="' + undefined + '">';
            },
            },
            {
                targets: 3, visible: true, render: function (data, type) {
                return '<select style="width:90px" class="choice_1" class="form-control"></select>';
            },
            },
            {
                targets: 4, visible: true, render: function (data, type) {
                return '<select style="width:90px" class="choice_2" class="form-control"></select>';
            },
            },
            {targets: 2, visible: false},
            {targets: 5, visible: false},
            {targets: 6, visible: false},
            {targets: 20, visible: false},
            {targets: 21, visible: false},
            {targets: 22, visible: false},
            {targets: 23, visible: false},
            {targets: 24, visible: false},
            {targets: 25, visible: false},
            {targets: 7, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 8, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 9, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 10, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 11, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 12, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 13, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 14, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 15, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 16, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 17, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
            {targets: 18, render: function(data) {return '<div style ="width:90px">'+data+'</div>'}},
        ],

        buttons: [
            {
                extend: 'excelHtml5',
                exportOptions: {
                    columns: [1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
                },
                text: 'Excel',
                filename: $("#pagetitle").text() + '-강좌관리',
            }
        ],
        language: {
                    lengthMenu: "_MENU_",
                    zeroRecords: "조회된 데이터가 없습니다",
                    info: "전체페이지 _PAGE_ / _PAGES_ ( _MAX_ )",
                    infoEmpty: "No records available",
                    infoFiltered: "(filtered from _MAX_ total records)",
                    sEmptyTable: "조회된 데이터가 없습니다",
                    paginate: {
                        first: "처음",
                        previous: "이전",
                        next: "다음",
                        last: "끝"
                    }
                },
        "initComplete": fnInitComplete
    });
}

$.datepicker.setDefaults({
    dateFormat: 'yy-mm-dd',
    prevText: '이전 달',
    nextText: '다음 달',
    monthNames: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    monthNamesShort: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    dayNames: ['일', '월', '화', '수', '목', '금', '토'],
    dayNamesShort: ['일', '월', '화', '수', '목', '금', '토'],
    dayNamesMin: ['일', '월', '화', '수', '목', '금', '토'],
    showMonthAfterYear: true,
    yearSuffix: '년'
});

var fnInitComplete = function () {

    console.log("initComplete2");

    var choice1 = [['001', '개발유형1'], ['002', '개발유형2'], ['003', '개발유형3'], ['004', '개발유형4'], ['005', '개발유형5']];
    var choice2 = [];

    var Year = new Date().getFullYear();
    for (var i = 0; i <= (Year - 2015); i++) {
        choice2.push(2015 + i);
    }
    var html1 = "<option value=''>선택하세요.</option>";
    var html2 = "<option value=''>선택하세요.</option>";

    for (var i = 0; i < choice1.length; i++) {
        html1 += "<option value=" + choice1[i][0] + ">" + choice1[i][1] + "</option>"
    }
    $('.choice_1').html(html1);

    for (var i = 0; i < choice2.length; i++) {
        html2 += "<option value=" + choice2[i] + ">" + choice2[i] + "</option>"
    }
    $('.choice_2').html(html2);


    $('.buttons-html5').attr('class', 'btn btn-default');
    $('input[type="checkbox"]').css("float", "right");

    $("#notice_body input[type=checkbox]:unchecked").each(function () {
        var $row;
        var data;
        var choice1;
        var choice2;
        var t = $('#datatable1').DataTable();

        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        choice1 = data[5];
        choice2 = data[6];

        $(this).parent().next().next().find("select").val(choice1).prop("selected", true);
        $(this).parent().next().next().next().find("select").val(choice2).prop("selected", true);

    });
    $('.choice_1').change(function () {
        $(this).parent().prev().prev().find('input:checkbox').prop("checked", true);
    });
    $('.choice_2').change(function () {
        $(this).parent().prev().prev().prev().find('input:checkbox').prop("checked", true);
    });

}

$(function () {
    $("#datepicker1, #datepicker2").datepicker();
});


function checked_all() {
    console.log($("#check_all").is(":checked"));

    if ($("#check_all").is(":checked")) {
        $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", true);
    } else {
        $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", false);
    }
}

function search() {
    var table = $('#datatable1').DataTable();
    table.ajax.reload(fnInitComplete);
}

function Save() {
    var $row;
    var data;
    var choice1;
    var choice2;
    var t = $('#datatable1').DataTable();
    var course_id = '';
    var choice1_list = '';
    var choice2_list = '';

    $("#notice_body input[type=checkbox]:checked").each(function () {

        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        choice1 = $(this).parent().next().next().find("select").val();
        choice2 = $(this).parent().next().next().next().find("select").val();

        course_id += data[2] + "$";
        choice1_list += choice1 + "$";
        choice2_list += choice2 + "$";
    });

    $.post("/manage/course_db/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        user_id: '{{ user.id }}',
        course_id: course_id,
        choice1_list: choice1_list,
        choice2_list: choice2_list,
        method: 'add',
    }).done(function (data) {
        search();
    }).fail(function (error) {
        swal("경고", "이미 추가된 강좌가 존재합니다.", "warning");
    });
}
function Del() {
    var $row;
    var data;
    var choice1;
    var choice2;
    var t = $('#datatable1').DataTable();
    var course_id = '';
    swal("경고", "실제 강좌는 삭제 되지 않고 추가 정보만 삭제됩니다.", "warning");

    $("#notice_body input[type=checkbox]:checked").each(function () {

        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        choice1 = $(this).parent().next().next().find("select").val();
        choice2 = $(this).parent().next().next().next().find("select").val();

        course_id += data[2] + "$";
    });

    $.post("/manage/course_db/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        user_id: '{{ user.id }}',
        course_id: course_id,
        method: 'del',
    }).done(function (data) {
        search();
    }).fail(function (error) {
        swal("경고", "이미 추가된 강좌가 존재합니다.", "warning");
    });
}

function display_date(value) {
    if (value != 0) {
        $('.date').css("display", "");
    }
    else if (value == 0) {
        $('.date').css("display", "none");
    }

}