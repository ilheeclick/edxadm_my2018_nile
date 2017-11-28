jQuery.ajaxSettings.traditional = true;

$(document).ready(function () {

    $('.summernote').summernote({
        lang: 'ko-KR',
        height: 400,
    });


    var value_list;
    var id = '{{id}}';
    if (id != 99999) {
        document.getElementById('DelBtn').style.display = '';
        document.getElementById('CopyBtn').style.display = '';
    }
    $.ajax({
        url: '/manage/modi_popup/' + id,
        data: {
            method: 'modi'
        }
    }).done(function (data) {
        value_list = data[0].toString().split(',');

        if (data[0][0] == "HTML") {
            $("#radio_1").attr('checked', 'checked');
            Display("Radio_HTML");
        }
        else if (data[0][0] == "Image") {
            $("#radio_2").attr('checked', 'checked');
            Display("Radio_IMAGE");
        }
        else {
            $("#radio_1").attr('checked', 'checked');
            Display("Radio_HTML");
        }

        if (data[0][1] == "없음") {
            $("#link_type").val("없음").prop("selected", true);
        }
        else if (data[0][1] == "전체링크") {
            $("#link_type").val("전체링크").prop("selected", true);
        }
        else if (data[0][1] == "이미지맵") {
            $("#link_type").val("이미지맵").prop("selected", true);
        }
        setValues();

        var image_maplist = data[0][2].split('/');
        for (var i = 0; i < image_maplist.length; i++) {
            if (i == 0) {
                $('.image_map').val(image_maplist[i]);
            }
            else {
                $("#location").append("<input type='text' value ='" + image_maplist[i] + "' style='margin: 0px 0px 5px 0px;' class='form-control image_map' placeholder='0.0.100.100'>");
            }
        }


        $('#title').val(data[0][3]);
        $('.summernote').summernote('code', data[0][4].replace(/\&\^\&/g));
        $('#image_URL').val(data[0][5]);
        $('#link_URL').val(data[0][6]);

        if (data[0][7] == "blank") {
            $("#link_target").val("blank").prop("selected", true);
        }
        else if (data[0][7] == "self") {
            $("#link_target").val("self").prop("selected", true);
        }

        $('#start_date').val(data[0][8]);
        $('#start_time').val(data[0][9]);
        $('#end_date').val(data[0][10]);
        $('#end_time').val(data[0][11]);

        if (data[0][12] == "없음") {
            $("#template").val("없음").prop("selected", true);
        }
        else if (data[0][12] == "type1") {
            $("#template").val("type1").prop("selected", true);
        }
        else if (data[0][12] == "type2") {
            $("#template").val("type2").prop("selected", true);
        }
        else if (data[0][12] == "type3") {
            $("#template").val("type3").prop("selected", true);
        }

        $('#width').val(data[0][13]);
        $('#height').val(data[0][14]);

        if (data[0][15] == "1일") {
            $("#hidden_day").val("1일").prop("selected", true);
        }
        else if (data[0][15] == "7일") {
            $("#hidden_day").val("7일").prop("selected", true);
        }
        else if (data[0][15] == "그만보기") {
            $("#hidden_day").val("그만보기").prop("selected", true);
        }

        if (data[0][16] == "Y") {
            $("#use_yn").val("사용함").prop("selected", true);
        }
        else if (data[0][16] == "N") {
            $("#use_yn").val("사용안함").prop("selected", true);
        }
    })
});

function Display(id) {
    if (id == "Radio_HTML") {
        document.getElementById('Radio_HTML').style.display = '';
        document.getElementById('Radio_IMAGE').style.display = 'none';
        document.getElementById('type1').style.display = '';
        document.getElementById('type2').style.display = '';
        document.getElementById('type3').style.display = '';
        document.getElementById('map').style.display = 'none';
    }
    else if (id == "Radio_IMAGE") {
        document.getElementById('Radio_HTML').style.display = 'none';
        document.getElementById('Radio_IMAGE').style.display = '';
        document.getElementById('type1').style.display = 'none';
        document.getElementById('type2').style.display = 'none';
        document.getElementById('type3').style.display = 'none';
        document.getElementById('map').style.display = '';
        $("#template").val("없음").prop("selected", true);

    }
}

function setValues() {
    var link_type = document.getElementById("link_type");

    if (link_type.options[link_type.selectedIndex].text == "없음") {
        document.getElementById('imagemap').style.display = 'none';
        document.getElementById('linkurl').style.display = 'none';
    }
    else if (link_type.options[link_type.selectedIndex].text == "전체링크") {
        document.getElementById('imagemap').style.display = 'none';
        document.getElementById('linkurl').style.display = '';
    }
    else if (link_type.options[link_type.selectedIndex].text == "이미지맵") {
        document.getElementById('imagemap').style.display = '';
        document.getElementById('linkurl').style.display = '';
    }
}

function Reset_check(){
    var r = confirm("작업내용 초기화 하시겠습니까?");
    if (r == true) {
        Reset();
    }
}

function Reset() {
    $('.image_map').val('');
    $('#title').val('');
    $('#image_URL').val('');
    $('#link_URL').val('');
    $('#start_date').val('');
    $('#start_time').val('12:00');
    $('#end_date').val('');
    $('#end_time').val('12:00');
    $('#width').val('');
    $('#height').val('');
    $('.summernote').summernote('code', '');
}

function copy() {
    try {
        var pop_id = '{{ id }}';
        $.post("/manage/new_popup/", {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            pop_id: pop_id,
            method: 'copy',
        }).done(function (data) {
            location.href = '/manage/modi_popup/' + data;
        }).fail(function (error) {
            alert('error = ' + error.responseJSON);
        });
    } catch (e) {
        alert(e);
    }
}
var file_flag = '0';
var update_flag = '0';
function save() {
    try {
        var popup_type = $("input[type=radio][name=radio]:checked").val();
        var uploadfile = $('#uploadfile').val();
        var pop_id = '{{ id }}';

        if (popup_type == "image") {
            $.post("/manage/new_popup/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                pop_id: pop_id,
                method: 'check',
            }).done(function (data) {
                update_flag = data;
                if (uploadfile == '' && data == '0') {
                    swal("경고", "이미지파일을 등록해주세요.", "warning");
                }
                else if ($('#title').val() == '') {
                    swal("경고", "제목을 입력해주세요.", "warning");
                }
                else if ($('#start_date').val() == '') {
                    swal("경고", "시작일을 입력해주세요.", "warning");
                }
                else if ($('#end_date').val() == '') {
                    swal("경고", "종료일을 입력해주세요.", "warning");
                }
                else if ($('#width').val() == '') {
                    swal("경고", "창너비를 입력해주세요.", "warning");
                }
                else if ($('#height').val() == '') {
                    swal("경고", "창높이를 입력해주세요.", "warning");
                }
                else if (uploadfile == '' && data == '1') {
                    save_data(pop_id);
                }
                else {
                    file_flag = '1';
                    document.getElementById("uploadform").submit();
                    save_data(pop_id);
                }

            }).fail(function (error) {
                alert('error = ' + error.responseJSON);
            });
        }
        else if (popup_type == "text") {

            if ($('#title').val() == '') {
                swal("경고", "제목을 입력해주세요.", "warning");
            }
            else if ($('#start_date').val() == '') {
                swal("경고", "시작일을 입력해주세요.", "warning");
            }
            else if ($('#end_date').val() == '') {
                swal("경고", "종료일을 입력해주세요.", "warning");
            }
            else if ($('#width').val() == '') {
                swal("경고", "창너비를 입력해주세요.", "warning");
            }
            else if ($('#height').val() == '') {
                swal("경고", "창높이를 입력해주세요.", "warning");
            }
            else {
                save_data(pop_id);
            }
        }
    } catch (e) {
        alert(e);
    }
}

function save_data(pop_id) {

    var pop_id = pop_id;
    var method = '';
    var id = '{{ id }}';
    if (id == 99999) {
        method = 'add';
    }
    else {
        method = 'modi';
    }
    var popup_type = $("input[type=radio][name=radio]:checked").val();
    if (popup_type == "image") {
        popup_type = "I";
    }
    else if (popup_type == "text") {
        popup_type = "H";
    }

    var link_type = document.getElementById("link_type");
    if (link_type.options[link_type.selectedIndex].text == "없음") {
        link_type = "0";
    }
    else if (link_type.options[link_type.selectedIndex].text == "전체링크") {
        link_type = "1";
    }
    else if (link_type.options[link_type.selectedIndex].text == "이미지맵") {
        link_type = "2";
    }

    var image_map = '';
    $('.image_map').each(function () {
        image_map += $(this).val() + "/";
    });
    var title = $('#title').val();
    var image_url = $('#image_URL').val();
    var link_url = $('#link_URL').val();
    var link_target = document.getElementById("link_target");
    if (link_target.options[link_target.selectedIndex].text == "blank") {
        link_target = "B";
    }
    else if (link_target.options[link_target.selectedIndex].text == "self") {
        link_target = "S";
    }

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
    var template = document.getElementById("template");
    if (template.options[template.selectedIndex].text == "없음") {
        template = "0";
    }
    else if (template.options[template.selectedIndex].text == "type1") {
        template = "1";
    }
    else if (template.options[template.selectedIndex].text == "type2") {
        template = "2";
    }
    else if (template.options[template.selectedIndex].text == "type3") {
        template = "3";
    }

    var width = $('#width').val();
    var height = $('#height').val();

    var hidden_day = document.getElementById("hidden_day");
    if (hidden_day.options[hidden_day.selectedIndex].text == "그만보기") {
        hidden_day = "0";
    }
    else if (hidden_day.options[hidden_day.selectedIndex].text == "1일") {
        hidden_day = "1";
    }
    else if (hidden_day.options[hidden_day.selectedIndex].text == "7일") {
        hidden_day = "7";
    }

    var regist_id = '{{ user.id }}';
    var contents = $('.summernote').summernote('code');

    var use_yn = document.getElementById("use_yn");
    if (use_yn.options[use_yn.selectedIndex].text == "사용함") {
        use_yn = "Y";
    }
    else if (use_yn.options[use_yn.selectedIndex].text == "사용안함") {
        use_yn = "N";
    }

    $.ajax({
        url: '/manage/modi_popup/' + '77777',
        data: {
            method: 'modi'
        }
    }).done(function (data) {
        if (method == 'modi') {
            if (data >= 3 && use_yn == "N") {
                alert("현재 사용중인 팝업창" + data + "개 입니다.(사용안함으로 저장됩니다.)");
                use_yn = "N";
            }
        }
        else if (method == 'add') {
            if (data >= 3) {
                alert("현재 사용중인 팝업창" + data + "개 입니다.(사용안함으로 저장됩니다.)");
                use_yn = "N";
            }
        }
        $.post("/manage/new_popup/", {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            pop_id: pop_id,
            popup_type: popup_type,
            link_type: link_type,
            image_map: image_map,
            title: title,
            contents: contents,
            image_url: image_url,
            link_url: link_url,
            link_target: link_target,
            start_date: start_date,
            start_time: start_time,
            end_date: end_date,
            end_time: end_time,
            template: template,
            width: width,
            height: height,
            hidden_day: hidden_day,
            regist_id: regist_id,
            use_yn: use_yn,
            file_flag: file_flag,
            update_flag: update_flag,
            method: method,
        }).done(function (data) {
            location.href = '/manage/popup_db';
        }).fail(function (error) {
            alert('error = ' + error.responseJSON);
        });
    });

}

function del() {
    try {
        var pop_id = '{{ id }}';
        $.post("/manage/new_popup/", {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            pop_id: pop_id,
            method: 'delete',
        }).done(function (data) {
            location.href = '/manage/popup_db';
        }).fail(function (error) {
            alert('error = ' + error.responseJSON);
        });
    } catch (e) {
        alert(e);
    }
}

jQuery.fn.center = function () {
    this.css("position", "absolute");
    this.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) + $(window).scrollTop()) + "px");
    this.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) + $(window).scrollLeft()) + "px");
    return this;
}

function preview() {
    var width = $('#width').val();
    var height = $('#height').val();
    if (template.options[template.selectedIndex].text == "type1") {
        window.open("/manage/popup_index1/" + '{{id}}', null,
            "height=" + height + ",width=" + width + ",status=yes,toolbar=no,menubar=no,location=no");
    }
    else if (template.options[template.selectedIndex].text == "type2") {
        window.open("/manage/popup_index2/" + '{{id}}', null,
            "height=" + height + ",width=" + width + ",status=yes,toolbar=no,menubar=no,location=no");
    }
    else if (template.options[template.selectedIndex].text == "type3") {
        window.open("/manage/popup_index3/" + '{{id}}', null,
            "height=" + height + ",width=" + width + ",status=yes,toolbar=no,menubar=no,location=no");
    }

}

var link_url = $('#link_URL').val();

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
    //  $("#start_time, #end_time").timepicker();
});

$("#start_time, #end_time").timepicker({
    'timeFormat': 'HHmm',
    showMeridian: false,
    minuteStep: 1,
});

var add_location_cnt = 1;
function add_location() {
    if (add_location_cnt < 5) {
        $("#location").append("<input type='text' style='margin: 0px 0px 5px 0px;' class='form-control image_map' placeholder='0.0.100.100'>");
    }
    else {
        swal("경고", "최대 5개까지 등록 가능합니다.", "warning");
    }
    add_location_cnt += 1;
}

