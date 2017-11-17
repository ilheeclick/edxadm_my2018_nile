jQuery.ajaxSettings.traditional = true;
$(document).ready(function(){
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

            $('#image_map').val(data[0][2]);
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
            else if (data[0][12] == "기본") {
                $("#template").val("기본").prop("selected", true);
            }
            else if (data[0][12] == "중간템플릿") {
                $("#template").val("중간템플릿").prop("selected", true);
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


    function Display(id)
    {
       if(id == "Radio_HTML")
       {
          document.getElementById('Radio_HTML').style.display = '';         // 보이게
          document.getElementById('Radio_IMAGE').style.display = 'none';  // 안보이게
       }
       else if(id == "Radio_IMAGE")
       {
          document.getElementById('Radio_HTML').style.display = 'none';  // 안보이게
          document.getElementById('Radio_IMAGE').style.display = '';         // 보이게
       }
    }


    function setValues() {
        var link_type = document.getElementById("link_type");

        if(link_type.options[link_type.selectedIndex].text == "없음") {
            document.getElementById('imagemap').style.display = 'none';
            document.getElementById('linkurl').style.display = 'none';
        }
        else if (link_type.options[link_type.selectedIndex].text =="전체링크") {
            document.getElementById('imagemap').style.display = 'none';
            document.getElementById('linkurl').style.display = '';
        }
        else if (link_type.options[link_type.selectedIndex].text == "이미지맵"){
            document.getElementById('imagemap').style.display = '';
            document.getElementById('linkurl').style.display = '';
        }
    }

    function Reset() {
        $('#image_map').val('');
        $('#title').val('');
        $('#image_URL').val('');
        $('#link_URL').val('');
        $('#start_date').val('');
        $('#start_time').val('');
        $('#end_date').val('');
        $('#end_time').val('');
        $('#width').val('');
        $('#height').val('');
        $('.summernote').summernote('code', '');
    }