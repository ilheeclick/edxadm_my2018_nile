var file_name, file_ext, file_size;
//신규 등록
$('#knews_save').on('click', function(e){
    try{
        //alert(file_name+'/'+file_ext+'/'+file_size);
        var action_mode;
        var knews_title, knews_content, uploadfile;
        uploadfile = $('#uploadfile').val().substr(12);
        knews_title = $('#noticetitle').val();
        knews_content = $('.summernote').summernote('code');
        action_mode = 'add';
        var head_title = $('#head_title').find('option:selected').attr('id');
        //noticecontent = $('#noticecontent').val();
        //alert(noticetitle + ' / '  + noticecontent);

        if(head_title == 'null'){
            head_title = ''
        }
        /* insert to database */
        $.post("/manage/new_knews/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            knews_title: knews_title,
            knews_content: knews_content,
            head_title : head_title,
            uploadfile: uploadfile,
            file_name: file_name,
            file_ext: file_ext,
            file_size: file_size,
            k_news: 'K',
            method: action_mode
        }).done(function(data){
            location.href='/manage/comm_k_news';
        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});

$(document).on('click', '#fileupload', function(){

    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/manage/new_knews',
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
            alert("업로드에 성공했습니다.");
            file_name=adata[0];
            file_ext=adata[1];
            file_size=adata[2]
        },
        error: function() {
            alert("업로드에 실패했습니다.");
        }
    })
});




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

