$(function () {
  temp = ''
  $("#profit").mousemove(function () {
    mds_img_idx = $("#profit, .bk-canvas-overlays")
    mds_img_idx = mds_img_idx.children().find('span').html()
    mds_img_idx = mds_img_idx.substr(0, 7)
    if (temp != mds_img_idx) {
      $.getJSON('/ajax_list/' + mds_img_idx, function (ret) {
        $("#mds").html(ret.div + ret.script);
      })
      temp = mds_img_idx;
    }
  })
});
