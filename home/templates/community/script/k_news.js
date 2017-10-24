var file_name= [];
var file_ext= [];
var file_size= [];
jQuery.ajaxSettings.traditional = true;

// create new board
$('#knews_save').on('click', function(e){
    try{
        var action_mode;
        var knews_title, knews_content, uploadfile;
        var head_title = $('#head_title').find('option:selected').attr('id');
        knews_title = $('#noticetitle').val();
        knews_content = $('.summernote').summernote('code');
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
        $.post("/manage/new_knews/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            knews_title: knews_title,
            knews_content: knews_content,
            head_title : head_title,
            uploadfile: file_list,
            k_news: 'K',
            method: action_mode,
            odby: odby
        }).done(function(data){
            location.href='/manage/comm_k_news';
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
/*
$(document).on('click', '#fileupload', function(){
    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/manage/new_knews/',
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
*/

$(document).ready(function(){
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
                //console.log(data);
                $("#summernote").summernote("insertImage", data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus+' '+errorThrown);
            }
        });
    }
});

