$(document).ready(function () {
    $('.summernote').summernote({
        lang: 'ko-KR',
        height: 400,
    });
    $("#radio_1").attr('checked', 'checked');
});


function save() {
    var series_id = $('#series_id').val();
    var series_name = $('#series_name').val();
    var sumnail_file_id = $('#sumnail_file_id').val();
    var note = $('.summernote').summernote('code');
    var user_id = '{{ user.id }}';
    var use_yn = $("input[type=radio][name=radio]:checked").val();

    $.post("/manage/modi_series_course/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        series_id: series_id,
        series_name: series_name,
        sumnail_file_id: sumnail_file_id,
        note: note,
        user_id: user_id,
        use_yn: use_yn,
        method: 'add',
    }).done(function (data) {
        location.href = '/manage/series_course';
    }).fail(function (error) {
        alert('errorasdfasf = ' + error.responseJSON);
    });
}

