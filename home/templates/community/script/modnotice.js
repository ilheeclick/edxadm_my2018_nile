var file_name= [];
var file_ext= [];
var file_size= [];
jQuery.ajaxSettings.traditional = true;
$(document).ready(function(){
    var value_list;
    var id = '{{id}}';
    var use_yn = '{{use_yn}}';
    var html = "";
    $('.summernote').summernote({
        lang : 'ko-KR',
        height : 400,
        callbacks : {
            onImageUpload: function (files, modules, editable){
            sendFile(files[0], modules, editable);
           }
        }
    });
    function sendFile(file, modules, editable) {
        data = new FormData();
        data.append("file", file);
        $.ajax({
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            type: 'POST',
            url: '/manage/summer_upload/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            success: function(data){
                console.log(data);
                $("#summernote").summernote("insertImage", data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus+' '+errorThrown);
            }
        });
    }

    $.ajax({
        url : '/manage/modi_notice/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        //console.log(value_list);
        console.log(data);
        if(data[4] != null){
            value_list = data[4].toString().split(',');
            for(var i=0;i<value_list.length;i++){
                html += "<li><a href='#' id='download'>"+value_list[i]+"</a> <button class='btn btn-default' id='delete'>X</button></li>";
            }
            $('#saved_file').html(html);
        }
        $('#noticetitle').val(data[0]);
        $('.summernote').summernote('code', data[1].replace(/\&\^\&/g));
        $('#odby').val(data[2]);
        if(data[3] == ''){
            $('#head_title').val('선택하세요.');
        }else{
            $('#head_title').val(data[3]);
        }

    })
});

//파일 삭제 처리
$(document).on('click', '#delete', function(){
    var del_file = $(this).parent().text().slice(0, -2);
    var board_id = '{{id}}';
    $.post("/manage/new_notice/", {
        csrfmiddlewaretoken:$.cookie('csrftoken'),
        method : 'delete_file',
        board_id : board_id,
        del_file : del_file
    });
});

//파일 다운로드
$(document).on('click', '#saved_file > li > a', function(){
    var file_name = $(this).text();
    var board_id = '{{id}}';
    var use_yn = '{{use_yn}}';

    alert('/manage/modi_notice/'+board_id+'/'+use_yn + " : " + file_name);

    $.ajax({
        url : '/manage/modi_notice/'+board_id+'/'+use_yn,
            data : {
                method : 'file_download',
                file_name : file_name
            }
    }).done(function(data){
        window.open(data,'_blank');
    });
});


//수정 처리
$('#notice_mod').on('click', function(e){
    try{
        var action_mode;
        var noticetitle, noticecontent, notice, noti_id, odby;
        var uploadfile = $('#uploadfile').val().substr(12);
        var head_title =  $('#head_title').find('option:selected').attr('id');

        noticetitle = $('#noticetitle').val();
        noticecontent = $('.summernote').summernote('code');
        odby = $('#odby').val();
        action_mode = 'modi';
        noti_id = '{{id}}';

        if(head_title == 'null'){
            head_title = ''
        }
        /* insert to database */
        $.post("/manage/new_notice/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: noticetitle,
            nt_cont: noticecontent,
            noti_id : noti_id,
            head_title : head_title,
            uploadfile : uploadfile,
            file_name : file_name,
            file_ext : file_ext,
            file_size : file_size,
            notice: 'N',
            odby: odby,
            method: action_mode
        }).done(function(data){
            location.href='/manage/comm_notice';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});
//파일 업로드
$(document).on('click', '#fileupload', function(){
    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/manage/new_notice/',
        beforeSubmit: function (data,form,option) {
            if( $("#uploadfile").val() != "" ){

                var ext = $('#uploadfile').val().split('.').pop().toLowerCase();

                //if($.inArray(ext, ['xls','xlsx']) == -1) {
                //    alert('xls,xlsx 파일만 업로드 할수 있습니다.');
                //    return false;
                //}
            }else{
                alert('파일을 선택한 후 업로드 버튼을 눌러 주십시오.');
                return false;
            }
        },
        success: function(adata){
            //성공후 서버에서 받은 데이터 처리
            //alert("업로드에 성공했습니다.");
            file_name.push(adata[0]);
            file_ext.push(adata[1]);
            file_size.push(adata[2]);
            $('#file_array').append('<input type="file" name="file" id = "uploadfile" />');
        },
        error: function() {
            alert("업로드에 실패했습니다.");
        }
    })
});


//숨김 처리
$('#notice_del').on('click', function(){
    var id = '{{id}}';
    var use_yn = '{{use_yn}}';

    $.ajax({
        url:'/manage/comm_notice/',
        data:{
            noti_id:id,
            use_yn:use_yn,
            method:'notice_del'
        }
    }).done(function(data){
        console.log(data);
        location.href='/manage/comm_notice'
    });
});

//삭제 처리
$('#notice_delete').on('click', function(){
    var id = '{{id}}';
    var use_yn = '{{use_yn}}';

    $.ajax({
        url:'/manage/comm_notice/',
        data:{
            noti_id:id,
            use_yn:use_yn,
            method:'notice_delete'
        }
    }).done(function(data){
        console.log(data);
        location.href='/manage/comm_notice'
    });
});
