var file_name, file_ext, file_size;
$(document).ready(function(){
    var value_list;
    var id = {{id}}
    var use_yn = '{{use_yn}}';
    var html = "";
    $.ajax({
        url : '/modi_refer/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){

        if(data[3] != null){
            value_list = data[3].toString().split(',');
            for(var i=0;i<value_list.length;i++){
                html += "<a href='#' id='download' >"+value_list[i]+"</a>" +
                "<br>";
            }
            $('#saved_file').html(html);
        }
        $('#refertitle').val(data[0]);
        $('.summernote').summernote('code', data[1].replace(/\&\^\&/g));
        $('#odby').val(data[2]);
    })
});

//파일 다운로드
$(document).on('click', '#saved_file > a', function(){
    var file_name = $(this).text();
    var board_id = {{id}};
    var use_yn = '{{use_yn}}';

    $.ajax({
        url : '/modi_refer/'+board_id+'/'+use_yn,
            data : {
                method : 'file_download',
                file_name : file_name
            }
    }).done(function(data){
        $("#download").prop("href", data);
        location.href=$("#download").attr('href');
    });
});


//수정 처리
$('#refer_mod').on('click', function(e){
    try{
        var action_mode;
        var refertitle, refercontent, refer, refer_id, odby;
        var uploadfile = $('#uploadfile').val().substr(12);
        refertitle = $('#refertitle').val();
        refercontent = $('.summernote').summernote('code');
        odby = $('#odby').val();
        action_mode = 'modi';
        refer_id = {{ id }}
        //alert('file_name =='+file_name);
        //alert('file_ext =='+file_ext);
        //alert('file_size =='+file_size);

        /* insert to database */
        $.post("/new_refer/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            refer_title: refertitle,
            refer_cont: refercontent,
            refer_id : refer_id,
            uploadfile : uploadfile,
            file_name : file_name,
            file_ext : file_ext,
            file_size : file_size,
            refer: 'R',
            odby: odby,
            method: action_mode
        }).done(function(data){
            location.href='/comm_reference_room';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});
//삭제 처리
$('#refer_del').on('click', function(){
    var id = {{id}}
    var use_yn = '{{use_yn}}';

    $.ajax({
        url:'/comm_reference_room/',
        data:{
            refer_id:id,
            use_yn:use_yn,
            method:'refer_del'
        }
    }).done(function(data){
        console.log(data);
        location.href='/comm_reference_room'
    });
});

//파일 업로드
$(document).on('click', '#fileupload', function(){
    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/new_notice/',
        beforeSubmit: function (data,form,option) {
            if( $("#uploadfile").val() != "" ){

                var ext = $('#uploadfile').val().split('.').pop().toLowerCase();

                if($.inArray(ext, ['xls','xlsx', 'txt', 'hwp', 'pptx', 'jpg']) == -1) {
                    //alert('xls,xlsx 파일만 업로드 할수 있습니다.');
                    alert('정해진 파일 형식만 업로드 할수 있습니다.');
                    return false;
                }
            }else{
                alert('파일을 선택한 후 업로드 버튼을 눌러 주십시오.');
                return false;
            }
        },
        success: function(adata){
            //성공후 서버에서 받은 데이터 처리
            alert("업로드에 성공했습니다.");
            console.log(adata);
            file_name=adata[0];
            file_ext=adata[1];
            file_size=adata[2];
            console.log('file_name', file_name, 'file_ext', file_ext, 'file_size', file_size)

        },
        error: function() {
            alert("업로드에 실패했습니다.");
            alert(error);
        }
    })
});