//페이지 로드
//var noti_page;
//$(document).ready(function(){
//    //var search_con = $('#search option:selected').attr('id');
//    //var search_search = $('#textarea').val();
//    var value_list;
//    var action_mode="notice_list";
//    var html;
//    var total_page;
//
//    //total_page 로드
//    $.ajax({
//        url: '/comm_notice/',
//        data:{
//            method : 'total_page',
//        }
//    }).done(function(data){
//        total_page = data[0];
//        //page 소스
//        var obj = $('#pagination').twbsPagination({
//            visiblePages: 5,
//            totalPages: total_page,
//            onPageClick: function (event, page) {
//                html = "";
//                console.info(page);
//                noti_page = page;
//                $.ajax({
//                    url:'/comm_notice/',
//                        data:{
//                            method: 'notice_list',
//                            page: page
//                        }
//                }).done(function (data) {
//                    value_list = data[0].toString().split(',');
//                    for(var i=0; i<data.length; i++){
//                        html+='<tr id="notice_tr">'
//                        for(var j=0; j<value_list.length; j++){
//                            if(j==0){
//                                //html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+data[i][j]+'</td>'
//                                html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+(i+1)+'</td>'
//                            }
//                            else if(j==1){
//                                html+='<td id="title"><a href="/modi_notice/'+data[i][j-1]+'">'+data[i][j]+'</a></td>'
//                            }
//                            else{
//                                html+='<td>'+data[i][j]+'</td>'
//                            }
//                        }
//                        html+='</tr>'
//                    }
//                    $('#notice_body').html(html);
//                });
//            }
//        });
//    });
//});


//검색
//$('#search_notice').on('click', function(){
//    var search_con = $('#search option:selected').attr('id');
//    var search_search = $('#textarea').val();
//    var value_list;
//    var action_mode="notice_list";
//    var html;
//
//    html = "";
//    //alert(search_con + " / " + search_search);
//    $.ajax({
//        url:'/comm_notice/',
//            data:{
//                method: action_mode,
//                search_con : search_con,
//                search_search : search_search,
//                page : noti_page
//            }
//    }).done(function (data) {
//        value_list = data[0].toString().split(',');
//        for(var i=0; i<data.length; i++){
//            html+='<tr id="notice_tr">'
//            for(var j=0; j<value_list.length; j++){
//                if(j==0){
//                    html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+data[i][j]+'</td>'
//                }
//                else if(j==1){
//                    html+='<td id="title"><a href="/modi_notice/'+data[i][j-1]+'">'+data[i][j]+'</a></td>'
//                }
//                else{
//                    html+='<td>'+data[i][j]+'</td>'
//                }
//            }
//            html+='</tr>'
//        }
//        $('#notice_body').html(html);
//    });
//});
var file_name, file_ext, file_size;
//신규 등록
$('#notice_save').on('click', function(e){
    try{
        alert(file_name+'/'+file_ext+'/'+file_size);
        var action_mode;
        var noticetitle, noticecontent, notice, uploadfile;
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




