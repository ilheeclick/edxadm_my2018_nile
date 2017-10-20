var file_name= [];
var file_ext= [];
var file_size= [];
jQuery.ajaxSettings.traditional = true;
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
                $("#summernote").summernote("insertImage", data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus+' '+errorThrown);
            }
        });
    }
});
//신규 등록
$('#refer_save').on('click', function(e){
    try{
        var action_mode;
        var refertitle, refercontent, notice, uploadfile;
        action_mode = 'add';
        uploadfile = $('#uploadfile').val().substr(12);
        refertitle = $('#refertitle').val();
        var head_title = $('#head_title').find('option:selected').attr('id');
        refercontent = $('.summernote').summernote('code');
        odby = $('#odby').val();

        if(refertitle != '' && refercontent != ''){
            if(head_title == 'null'){
                head_title = ''
            }

            /* insert to database */
            $.post("/manage/new_refer/", {
                csrfmiddlewaretoken:$.cookie('csrftoken'),
                refer_title: refertitle,
                refer_cont: refercontent,
                head_title : head_title,
                uploadfile: uploadfile,
                file_name: file_name,
                file_ext: file_ext,
                file_size: file_size,
                refer: 'R',
                method: action_mode,
                odby: odby
            }).done(function(data){
                location.href='/manage/comm_reference_room';
            }).fail(function(error) {
                alert('error = ' + error.responseJSON);
            });
        }else{
            alert('필수정보를 입력해주세요.');
        }
    }catch(e){
        alert(e);
    }
});

$(document).on('click', '#fileupload', function(){

    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/manage/new_refer/',


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




