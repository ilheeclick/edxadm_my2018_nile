var method = '';

$(document).ready(function () {
    if ('{{id}}' == '') {
        method = 'add';
    }
    else {
        method = 'modi';
    }
    $('.summernote').summernote({
        lang: 'ko-KR',
        height: 400,
    });
    $("#radio_1").attr('checked', 'checked');
    $.ajax({
        url: '/manage/modi_series/' + '{{ id }}',
        data: {
            method: 'modi_list'
        }
    }).done(function (data) {
        if (data != '') {
            $('#series_id').val(data[0][0]);
            $('#series_name').val(data[0][1]);
            $('.summernote').summernote('code', data[0][2].replace(/\&\^\&/g));
            if (data[0][3] == "Y") {
                $('#radio_1').attr('checked', 'checked');
            }
            else {
                $('#radio_2').attr('checked', 'checked');
            }
        }
    })
});


var file_flag = '0';
var update_flag = '0';
function save() {
    var sumnail_file_id = $('#sumnail_file_id').val();
    $.post("/manage/modi_series_course/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        series_seq: '{{id}}',
        method: 'check',
    }).done(function (data) {
        update_flag = data;

        if ($('#series_id').val() == '') {
            swal("경고", "시리즈 ID를 입력해주세요.", "warning");
        }
        else if ($('#series_name').val() == '') {
            swal("경고", "시리즈 명을 입력해주세요.", "warning");
        }
        else if (sumnail_file_id == '' && data == '0') {
            swal("경고", "썸네일 img를 등록해주세요.", "warning");
        }
        else if ($('.summernote').summernote('code') == '') {
            swal("경고", "시리즈 강좌소개를 입력해주세요.", "warning");
        }
        else if (sumnail_file_id == '' && data == '1') {
            Save_info();
        }
        else {
            file_flag = '1';
            document.getElementById("uploadform").submit();
            Save_info();
        }

    }).fail(function (error) {
        alert('errorasdfasf = ' + error.responseJSON);
    });
}

function Save_info() {
    var series_id = $('#series_id').val();
    var series_name = $('#series_name').val();
    var note = $('.summernote').summernote('code');
    var user_id = '{{ user.id }}';
    var use_yn = $("input[type=radio][name=radio]:checked").val();

    $.post("/manage/modi_series_course/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        series_id: series_id,
        series_name: series_name,
        note: note,
        user_id: user_id,
        use_yn: use_yn,
        series_seq: '{{id}}',
        file_flag: file_flag,
        update_flag: update_flag,
        method: method,
    }).done(function (data) {
        location.href = '/manage/series_course';
    }).fail(function (error) {
        alert('errorasdfasf = ' + error.responseJSON);
    });

}


function Del() {

    $.post("/manage/modi_series_course/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        series_seq: '{{id}}',
        method: 'delete',
    }).done(function (data) {
        location.href = '/manage/series_course';
    }).fail(function (error) {
        alert('errorasdfasf = ' + error.responseJSON);
    });
}

