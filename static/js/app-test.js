var infofunc = function () {
    $.get("/model", function (data) {
        $("#usedmodel").html(data);
    });
    $.get("/ram", function (data) {
        $("#ramusage").html(data);
    });
    $.get("/cpu", function (data) {
        $("#cpuusage").html(data);
    });
    $.get("/gpu", function (data) {
        $("#gpuusage").html(data);
    });
}

setInterval(infofunc, 5000);

infofunc();

function send() {

    for (var i = 1; i <= 5; i++) {
        question = $('#q' + i).text().trim();
        useranswer = $('#i' + i).val();
        gradeelem = $('#g' + i);
        ask(question, useranswer, gradeelem);
    }

}

function ask(q, a, gradeelem) {
    $.ajax({
        url: '/ask',
        data: {"question": q, "answer": a},
        type: 'POST',
        success: function (response) {
            data = JSON.parse(response);
            gradeelem.html(`${data.g} bodova!`);
            gradeelem.show()
        },
        error: function (error) {
            console.log(error);
        }
    });
}
