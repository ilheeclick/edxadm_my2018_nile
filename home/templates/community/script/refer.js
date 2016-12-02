
var file_name, file_ext, file_size;

$(document).ready(function(){
    $('.summernote').summernote({
        lang : 'ko-KR',
        height : 400,
    });
});
//신규 등록
$('#refer_save').on('click', function(e){
    try{
        //alert(file_name+'/'+file_ext+'/'+file_size);
        var action_mode;
        var refertitle, refercontent, notice, uploadfile;
        uploadfile = $('#uploadfile').val().substr(12);
        refertitle = $('#refertitle').val();
        //noticecontent = $('#noticecontent').val();
        refercontent = $('.summernote').summernote('code');
        //alert(noticetitle + ' / '  + noticecontent);
        action_mode = 'add';
        if(refertitle != '' && refercontent != ''){
            /* insert to database */
            $.post("/new_refer/", {
                csrfmiddlewaretoken:$.cookie('csrftoken'),
                refer_title: refertitle,
                refer_cont: refercontent,
                uploadfile: uploadfile,
                file_name: file_name,
                file_ext: file_ext,
                file_size: file_size,
                refer: 'R',
                method: action_mode
            }).done(function(data){
                location.href='/comm_reference_room';
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
        url:'new_refer',


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




