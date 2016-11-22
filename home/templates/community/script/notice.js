
var file_name, file_ext, file_size;
//신규 등록
$('#notice_save').on('click', function(e){
    try{
        //alert(file_name+'/'+file_ext+'/'+file_size);
        var action_mode;
        var noticetitle, noticecontent, notice, uploadfile;
        var head_title =  $('#head_title').find('option:selected').val();
        uploadfile = $('#uploadfile').val().substr(12);
        noticetitle = $('#noticetitle').val();
        //noticecontent = $('#noticecontent').val();
        noticecontent = $('.summernote').summernote('code');
        //alert(noticetitle + ' / '  + noticecontent);
        action_mode = 'add';

        /* insert to database */
        $.post("/new_notice/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: noticetitle,
            nt_cont: noticecontent,
            head_title: head_title,
            uploadfile: uploadfile,
            file_name: file_name,
            file_ext: file_ext,
            file_size: file_size,
            notice: 'N',
            method: action_mode
        }).done(function(data){
            location.href='/comm_notice';
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
        url:'new_notice',


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
            alert(error);
        }
    })
});




