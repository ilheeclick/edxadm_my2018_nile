$(document).ready(function() {

    $('#datatable1').DataTable({
        dom: '<"toolbar"><"search">rt<"bottom"ip><"clear">',
        "autoWidth": false,
        scrollX: true,
        bProcessing: true,
        ordering: false,
        serverSide: false,
        searching: true,
    });
} );