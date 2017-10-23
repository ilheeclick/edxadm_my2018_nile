var file_name= [];
var file_ext= [];
var file_size= [];
jQuery.ajaxSettings.traditional = true;
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
            $("#summernote").summernote("insertImage", data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus+' '+errorThrown);
        }
    });
}

// create new board
$('#notice_save').on('click', function(e){
    try{
        var action_mode;
        var noticetitle, noticecontent, notice, uploadfile;
        var head_title =  $('#head_title').find('option:selected').attr('id');
        noticetitle = $('#noticetitle').val();
        noticecontent = $('.summernote').summernote('code');
        action_mode = 'add';
        odby = $('#odby').val();
        if(head_title == 'null'){
            head_title = ''
        }

        // get file
        var file_list = "";
        file_cnt = $('#file_cnt').text();
        for(i=0; i<file_cnt; i++){
            item = '#file_'+i;
            file_list += ($(item).text());
            file_list += '+';
        }

        // ajax new board
        $.post("/manage/new_notice/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: noticetitle,
            nt_cont: noticecontent,
            head_title: head_title,
            uploadfile: file_list,
            notice: 'N',
            method: action_mode,
            odby: odby
        }).done(function(data){
            location.href='/manage/comm_notice';
        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});

// file upload
$(document).on('click', '#fileupload', function(){
    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/manage/new_notice/',
        beforeSubmit: function (data,form,option) {
            if( $("#uploadfile").val() != "" ){
                var ext = $('#uploadfile').val().split('.').pop().toLowerCase();
            }else{
                swal("업로드 경고", "파일을 선택한 후 업로드 버튼을 눌러 주십시오", "warning");
                return false;
            }
        },
        success: function(data){
            for(i=0; i<data.len; i++){
                $( "#file_array" ).append("<div id = 'file_" + i + "'>"+ data.name[i] + "&nbsp; &nbsp;" + data.size[i] +"</div>");
            }
            $( "#file_array" ).append("<div id = 'file_cnt' style = 'display:none'>"+ data.len +"</h5>");
            swal("업로드 완료", "OK 버튼을 눌러주세요", "success");
        },
        error: function() {
            swal("업로드 실패", "다시 시도해주세요", "error");
        }
    })
});
