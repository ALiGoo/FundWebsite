$(function () {
  var response_data;
  $.getJSON('/mds_img/', function (ret) {
    response_data = ret;
  })

  var temp = ''
  $("#profit").mousemove(function () {
    mds_img_idx = $("#profit, .bk-canvas-overlays")
    mds_img_idx = mds_img_idx.children().find('span').html()
    mds_img_idx = mds_img_idx.substr(0, 7)
    if (temp != mds_img_idx) {
      $("#mds").html(response_data[mds_img_idx].div + response_data[mds_img_idx].script);
      temp = mds_img_idx;
    }
  })
});
