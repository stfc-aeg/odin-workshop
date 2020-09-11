api_version = '0.1';

$( document ).ready(function() {

    update_api_version();
    update_api_adapters();
    poll_update()
});

function poll_update() {
    update_background_task();
    setTimeout(poll_update, 500);   
}

function update_api_version() {

    $.getJSON('/api', function(response) {
        $('#api-version').html(response.api);
        api_version = response.api;
    });
}

function update_api_adapters() {

    $.getJSON('/api/' + api_version + '/adapters/', function(response) {
        adapter_list = response.adapters.join(", ");
        $('#api-adapters').html(adapter_list);
    });
}

function update_background_task() {

    $.getJSON('/api/' + api_version + '/workshop/background_task', function(response) {
        var task_count_ioloop = response.background_task.ioloop_count;
        var task_count_thread = response.background_task.thread_count;
        var task_enabled = response.background_task.enable;
        $('#task-count-ioloop').html(task_count_ioloop);
        $('#task-count-thread').html(task_count_thread);
        $('#task-enable').prop('checked', task_enabled);
    });
}

function change_enable() {
    var enabled = $('#task-enable').prop('checked');
    console.log("Enabled changed to " + (enabled ? "true" : "false"));
    $.ajax({
        type: "PUT",
        url: '/api/' + api_version + '/workshop/background_task',
        contentType: "application/json",
        data: JSON.stringify({'enable': enabled})
    });
}
