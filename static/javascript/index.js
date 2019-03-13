$(function () {
    var page = 1
    $("#next_page").click(function () {
        page += 1
        $.getJSON("/index/page=" + page, function (ret) {
            var html = ""
            $.each(ret, function (i, item) {
                html += "<tr>\
                <td>" + item.fund_id + "</td>\
                <td>" + item.chinese_name + "</td>\
                <td>" + item.english_name + "</td>\
                <td>" + item.isin_code + "</td>\
                <td>" + item.entry_day + "</td>\
                <td>" + item.manager_fee + "</td>\
                <td>" + item.custody_fee + "</td>\
                <td>" + item.sales_fee + "</td>\
                <td>" + item.area + "</td>\
                </tr>"
            });
            $("#items").html(html);
        })
    });

    $("#prev_page").click(function () {
        page -= 1
        $.getJSON("/index/page=" + page, function (ret) {
            var html = ""
            $.each(ret, function (i, item) {
                html += "<tr>\
                <td>" + item.fund_id + "</td>\
                <td>" + item.chinese_name + "</td>\
                <td>" + item.english_name + "</td>\
                <td>" + item.isin_code + "</td>\
                <td>" + item.entry_day + "</td>\
                <td>" + item.manager_fee + "</td>\
                <td>" + item.custody_fee + "</td>\
                <td>" + item.sales_fee + "</td>\
                <td>" + item.area + "</td>\
                </tr>"
            });
            $("#items").html(html);
        })
    });
});
