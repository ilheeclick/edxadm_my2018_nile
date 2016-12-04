$(document).ready(function(){
    var value_list;
    var id = {{id}}
    var use_yn = '{{use_yn}}';
    $('.summernote').summernote({
        lang : 'ko-KR',
        height : 400,
    });
    $.ajax({
        url : '/modi_faq/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        //console.log(data)
        value_list = data[0].toString().split(',');
        //console.log(value_list);
        //$('.summernote1').summernote('code', value_list[0].replace(/\&\^\&/g, ','));
        $('#noticecontent').html(data[0][0]);
        $('.summernote').summernote('code',data[0][1].replace(/\&\^\&/g));
        $('#head_title').val(data[0][2])
    })
});

//수정 처리
$('#faq_mod').on('click', function(){
    try{
        var action_mode;
        var faq_question, faq_answer, faq_id;
        var head_title =  $('#head_title').find('option:selected').attr('id');
        faq_question = $('#noticecontent').val();
        faq_answer = $('.summernote').summernote('code');
        action_mode = 'modi';
        faq_id = {{ id }}
        if(head_title == 'null'){
            head_title='';
        }else{
            /* insert to database */
            $.post("/new_faq/", {
                csrfmiddlewaretoken:$.cookie('csrftoken'),
                faq_question: faq_question,
                faq_answer: faq_answer,
                faq_id : faq_id,
                head_title : head_title,
                notice: 'F',
                method: action_mode
            }).done(function(data){
                location.href='/comm_faq';

            }).fail(function(error) {
                alert('error = ' + error.responseJSON);
            });
        }
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