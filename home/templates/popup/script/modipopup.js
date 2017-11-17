jQuery.ajaxSettings.traditional = true;

    $(document).ready(function(){
        $.ajax({
            url: '/manage/modi_popup/' + '77777',
            data: {
                method: 'modi'
            }
        }).done(function (data) {
            if ( data >= 3 ) {
                swal("경고", "현재 사용중인 팝업창" + data +"개 입니다.", "warning");
            }
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

    function copy() {
        try {
            var pop_id = '{{ id }}';
                $.post("/manage/new_popup/", {
                    csrfmiddlewaretoken: $.cookie('csrftoken'),
                    pop_id: pop_id,
                    method: 'copy',
                }).done(function (data) {
                    location.href = '/manage/modi_popup/'+data;
                }).fail(function (error) {
                    alert('error = ' + error.responseJSON);
                });
        } catch (e) {
            alert(e);
        }
    }

    function save() {
        try {
            var uploadfile = $('#uploadfile').val();
            if (uploadfile == '') {
                swal("경고", "이미지파일을 등록해주세요.", "warning");
            }
            else {
                document.getElementById("uploadform").submit();
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
                    link_type = "0"
                }
                else if (link_type.options[link_type.selectedIndex].text == "전체링크") {
                    link_type = "1"
                }
                else if (link_type.options[link_type.selectedIndex].text == "이미지맵") {
                    link_type = "2"
                }

                var image_map = $('#image_map').val();
                var title = $('#title').val();
                var image_url = $('#image_URL').val();
                var link_url = $('#link_URL').val();
                var link_target = document.getElementById("link_target");
                if (link_target.options[link_target.selectedIndex].text == "blank") {
                    link_target = "B"
                }
                else if (link_target.options[link_target.selectedIndex].text == "self") {
                    link_target = "S"
                }

                var start_date = $('#start_date').val();
                var start_time = $('#start_time').val();
                var end_date = $('#end_date').val();
                var end_time = $('#end_time').val();
                var template = document.getElementById("template");
                if (template.options[template.selectedIndex].text == "없음") {
                    template = "0"
                }
                else if (template.options[template.selectedIndex].text == "기본") {
                    template = "1"
                }
                else if (template.options[template.selectedIndex].text == "중간템플릿") {
                    template = "2"
                }

                var width = $('#width').val();
                var height = $('#height').val();

                var hidden_day = document.getElementById("hidden_day");
                if (hidden_day.options[hidden_day.selectedIndex].text == "그만보기") {
                    hidden_day = "0"
                }
                else if (hidden_day.options[hidden_day.selectedIndex].text == "1일") {
                    hidden_day = "1"
                }
                else if (hidden_day.options[hidden_day.selectedIndex].text == "7일") {
                    hidden_day = "7"
                }

                var regist_id = '{{ user.id }}';
                var contents = $('.summernote').summernote('code');
                var pop_id = '{{ id }}';


                if (use_yn.options[use_yn.selectedIndex].text == "사용함") {
                    use_yn = "Y"
                }
                else if (use_yn.options[use_yn.selectedIndex].text == "사용안함") {
                    use_yn = "N"
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
                    method: method,
                }).done(function (data) {
                    location.href = '/manage/popup_db';
                }).fail(function (error) {
                    alert('error = ' + error.responseJSON);
                });
        }
        } catch (e) {
            alert(e);
        }
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
        this.css("position","absolute");
        this.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) + $(window).scrollTop()) + "px");
        this.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) + $(window).scrollLeft()) + "px");
        return this;
    }

    function preview() {
        var link_type = document.getElementById("link_type");
        var title = $('#title').val();
        var image_url = $('#image_URL').val();
        var link_target = document.getElementById("link_target");
        var width = $('#width').val();
        var height = $('#height').val();
        var contents = $('.summernote').summernote('code');

        if (link_target.options[link_target.selectedIndex].text == "blank") {
            link_target = "B"
        }
        else if (link_target.options[link_target.selectedIndex].text == "self") {
            link_target = "S"
        }
        if (template.options[template.selectedIndex].text == "없음") {
            $('#Popup_0').css("display","");
            $('#TITLE_0').html(title);
            $('#Popup_0').css("width",width);
            $('#Popup_0').css("height",height);
            $('#pop_0').attr("href", $('#link_URL').val());
            $('#IMG').attr('src',image_url);
            var max_width = width;
            var max_height = height;
            max_width = max_width - 10;
            max_height = max_height - 55;
            $('#IMG').css('width', max_width);
            $('#IMG').css('height', max_height);
            $('#CONTENTS_0').html(contents);
            $('#Popup_0').center();

        }
        else if (template.options[template.selectedIndex].text == "기본") {
            var link_target = document.getElementById("link_target");
            $('#Popup_1').css("display","");
            $('#TITLE_1').html(title);
            $('#CONTENTS_1').html(contents);
            $('#Popup_1').css("width",width);
            $('#Popup_1').css("height",height);
            $('#pop_1').attr("href", $('#link_URL').val()).attr("target","_"+ link_target.options[link_target.selectedIndex].text);;
            $('#Popup_1').center();
        }
        else if (template.options[template.selectedIndex].text == "중간템플릿") {
            var link_target = document.getElementById("link_target");
            $('#Popup_2').css("display","");
            $('#TITLE_2').html(title);
            $('#CONTENTS_2').html(contents);
            $('#Popup_2').css("width",width);
            $('#Popup_2').css("height",height);
            $('#pop_2').attr("href", $('#link_URL').val()).attr("target","_"+ link_target.options[link_target.selectedIndex].text);
            $('#Popup_2').center();
        }
    }

    var link_url = $('#link_URL').val();

    function fn_move(moveGbn){
        if(moveGbn == 'close'){
            $('#Popup_1').css("display","none");
            $('#Popup_2').css("display","none");
            $('#Popup_0').css("display","none");
        }
        else if(moveGbn == 'move') {
            window.open = ($('#link_URL').val());
        }
    }