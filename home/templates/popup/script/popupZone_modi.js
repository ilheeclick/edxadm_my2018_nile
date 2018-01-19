jQuery.ajaxSettings.traditional = true;

$(document).ready(function () {
    if ('{{id}}' != 'add') {
        document.getElementById('DelBtn').style.display = '';
    }
    $.ajax({
        url: '/modi_popupZone/' + '{{ id }}',
        data: {
            method: 'modi'
        }
    }).done(function (data) {
        $('#title').val(data[0][0]);
        $('#link_url').val(data[0][2]);
        $('#link_target').val(data[0][3]);
        $('#start_date').val(data[0][4]);
        $('#start_time').val(data[0][5]);
        $('#end_date').val(data[0][6]);
        $('#end_time').val(data[0][7]);
    });
});


var file_flag = '0';
var update_flag = '0';

function Save_btn() {
    if ('{{id}}' == 'add') {
        Save();
    }
    else {
        Modi();
    }
}

function Save() {
    var id = '{{id}}';
    var regist_id = '{{ user.id }}';
    var title = $('#title').val();
    var image_file = $('#image_file').val();
    var link_url = $('#link_url').val();
    var link_target = $('#link_target option:selected').val();
    var start_date = $('#start_date').val().replace("-", "").replace("-", "");
    var start_time = $('#start_time').val().replace(":", "");
    if (start_time.length == 3) {
        start_time = "0" + start_time;
    }
    var end_date = $('#end_date').val().replace("-", "").replace("-", "");
    var end_time = $('#end_time').val().replace(":", "");
    if (end_time.length == 3) {
        end_time = "0" + end_time;
    }

    if (title == '') {
        swal("경고", "제목을 입력해주세요.", "warning");
    }
    else if ((($('#start_date').val() > $('#end_date').val() || $('#start_date').val() == $('#end_date').val() && $('#start_time').val() > $('#end_time').val()))) {
        swal("경고", "올바른 게시기간을 입력해주세요.", "warning");
    }
    else if (image_file == '') {
        swal("경고", "이미지파일을 등록해주세요.", "warning");
    }
    else if (link_url == '') {
        swal("경고", "'Link_URL'을 입력해주세요.", "warning");
    }
    else if (start_date == '') {
        swal("경고", "시작일을 입력해주세요.", "warning");
    }
    else if (end_date == '') {
        swal("경고", "종료일을 입력해주세요.", "warning");
    }
    else {
        file_flag = '1';
        document.getElementById("uploadform").submit();

        $.post("/new_popupZone/", {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            title: title,
            link_url: link_url,
            link_target: link_target,
            start_date: start_date,
            start_time: start_time,
            end_date: end_date,
            end_time: end_time,
            regist_id: regist_id,
            file_flag: file_flag,
            method: 'add',
        }).done(function (data) {
            location.href = '/popupZone_db';
        }).fail(function (error) {
            alert('error = ' + error.responseJSON);
        });
    }
}

function Modi() {

    var id = '{{id}}';
    var regist_id = '{{ user.id }}';
    var title = $('#title').val();
    var image_file = $('#image_file').val();
    var link_url = $('#link_url').val();
    var link_target = $('#link_target option:selected').val();
    var start_date = $('#start_date').val().replace("-", "").replace("-", "");
    var start_time = $('#start_time').val().replace(":", "");
    if (start_time.length == 3) {
        start_time = "0" + start_time;
    }
    var end_date = $('#end_date').val().replace("-", "").replace("-", "");
    var end_time = $('#end_time').val().replace(":", "");
    if (end_time.length == 3) {
        end_time = "0" + end_time;
    }

    if (title == '') {
        swal("경고", "제목을 입력해주세요.", "warning");
    }
    else if ((($('#start_date').val() > $('#end_date').val() || $('#start_date').val() == $('#end_date').val() && $('#start_time').val() > $('#end_time').val()))) {
        swal("경고", "올바른 게시기간을 입력해주세요.", "warning");
    }
    else if (link_url == '') {
        swal("경고", "'Link_URL'을 입력해주세요.", "warning");
    }
    else {
        if (image_file != '') {
            file_flag = '1';
            document.getElementById("uploadform").submit();
        }
        $.post("/new_popupZone/", {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            title: title,
            link_url: link_url,
            link_target: link_target,
            start_date: start_date,
            start_time: start_time,
            end_date: end_date,
            end_time: end_time,
            regist_id: regist_id,
            file_flag: file_flag,
            seq: '{{ id }}',
            method: 'modi',
        }).done(function (data) {
            location.href = '/popupZone_db';
        }).fail(function (error) {
            alert('error = ' + error.responseJSON);
        });
    }

}

function Del() {
    $.post("/new_popupZone/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        seq: '{{ id }}',
        method: 'del',
    }).done(function (data) {
        location.href = '/popupZone_db';
    }).fail(function (error) {
        alert('error = ' + error.responseJSON);
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

$(function () {
    $("#start_date, #end_date").datepicker();
});

$("#start_time, #end_time").timepicker({
    'timeFormat': 'HHmm',
    showMeridian: false,
    minuteStep: 1,
});