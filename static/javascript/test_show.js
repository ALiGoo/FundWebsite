$(function () {
  var mds_img;
  $.getJSON('/mds_img/', function (ret) {
    mds_img = ret;
  })

  var temp = ''
  $("#profit").mousemove(function () {
    mds_img_idx = $("#profit, .bk-canvas-overlays")
    mds_img_idx = mds_img_idx.children().find('span').html()
    mds_img_idx = mds_img_idx.substr(0, 7)
    if (temp != mds_img_idx) {
      $("#mds").html(mds_img[mds_img_idx].div + mds_img[mds_img_idx].script);
      temp = mds_img_idx;
    }
  })
});
