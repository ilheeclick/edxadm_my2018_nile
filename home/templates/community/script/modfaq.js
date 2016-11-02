$(document).ready(function(){
    var value_list;
    var id = {{id}}
    var use_yn = '{{use_yn}}';
    $.ajax({
        url : '/modi_faq/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        value_list = data[0].toString().split(',');
        $('.summernote1').summernote('code', value_list[0].replace(/\&\^\&/g, ','));
        $('.summernote2').summernote('code', value_list[1].replace(/\&\^\&/g, ','));
    })
});

//수정 처리
$('#faq_mod').on('click', function(){
    try{
        var action_mode;
        var faq_question, faq_answer, faq_id;

        faq_question = $('.summernote1').summernote('code');
        faq_answer = $('.summernote2').summernote('code');
        action_mode = 'modi';
        faq_id = {{ id }}
        //alert(faq_question+' / '+faq_answer+' / '+noti_id);


        /* insert to database */
        $.post("/new_faq/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            faq_question: faq_question,
            faq_answer: faq_answer,
            faq_id : faq_id,
            notice: 'F',
            method: action_mode
        }).done(function(data){
            location.href='/comm_faq';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});

//삭제 처리
$('#del_faq').on('click', function(){
    var id = {{id}}
    var use_yn = '{{use_yn}}';

    $.ajax({
        url:'/comm_faq/',
        data:{
            faq_id:id,
            use_yn:use_yn,
            method:'faq_del'
        }
    }).done(function(data){
        console.log(data);
        location.href='/comm_faq'
    });
});