$(document).ready(() => {

    function getWordCount(jobId) {
        var url = "/results/" + jobId;

        var poller = () => {
        $.get(url, (data, status, xhr) => {
            console.log(xhr.status);
            console.log(data);
            if (xhr.status == 200) {
            $.each(data, (i, count) => {
                $("#word-count").append(
                $("<tr>").append(
                    $("<td>").text(count[0]),
                    $("<td>").text(count[1])
                )
                );
            });
            $("#submit-button").prop("disabled", false).text("Submit");
            $("#spinner").hide();
            } else {
            setTimeout(poller, 1000);
            }
        }).fail((err) => {
            console.log(err);
            $("#submit-button").prop("disabled", false).text("Submit");
            $("#spinner").hide();
            $("[role='alert']").show();
        });

        };
        
    poller();

    };

    var $form = $("[role='form']");
    $form.submit(event => {
        event.preventDefault();

        var postUrl = $form.attr("action");
        var inputUrl = $form.find('input[name="url"]').val();

        $.ajax({
        url: postUrl,
        type: "POST",
        contentType: "application/json",  // must explicitly specify for json.loads() to work
        data: JSON.stringify({ url: inputUrl }),
        success: jobId => {
            console.log(jobId);
            getWordCount(jobId);
            $("#word-count").html(null);
            $("#submit-button").prop("disabled", true).text("Loading...");
            $("#spinner").show();
            $("[role='alert']").hide();
        },
        error: err => console.log(err)
        });

    });

    });