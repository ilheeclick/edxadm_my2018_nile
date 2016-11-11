$(document).ready(function(){
    var value_list;
    var id = {{id}}
    var use_yn = '{{use_yn}}';
    $.ajax({
        url : '/modi_refer/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        value_list = data[0].toString().split(',');
        $('#refertitle').val(value_list[0]);
        $('.summernote').summernote('code', value_list[1].replace(/\&\^\&/g, ','));
        $('#odby').val(value_list[2]);
    })
});


//수정 처리
$('#refer_mod').on('click', function(e){
    try{
        var action_mode;
        var refertitle, refercontent, refer, refer_id, odby;


        refertitle = $('#refertitle').val();
        refercontent = $('.summernote').summernote('code');
        odby = $('#odby').val();
        action_mode = 'modi';
        refer_id = {{ id }}


        /* insert to database */
        $.post("/new_refer/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            refer_title: refertitle,
            refer_cont: refercontent,
            refer_id : refer_id,
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