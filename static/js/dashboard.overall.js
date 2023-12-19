function changeNode(id, txt, className) {
  const node = document.getElementById(id);
  node.innerText = txt;
  if (className) {
    node.classList.add(className);
  }
}

function incrementalTxt(val) {
  if (val < 0) {
    return "minus";
  } else if (val > 0) {
    return "plus";
  } else {
    return "unchanged";
  }
}

function initialStatOverall(stat) {
  /* 종합 - 사용자 수 값 */
  const user_cnt = stat[stat.length - 1]["user_count"];
  const enrol_user_cnt = stat[stat.length - 1]["enrolled_user_count"];
  const grad_user_cnt = stat[stat.length - 1]["graduated_user_count"];
  const guest_cnt = user_cnt - (enrol_user_cnt + grad_user_cnt);

  changeNode("user-total", user_cnt);
  changeNode("enrol-total", enrol_user_cnt);
  changeNode("grad-total", grad_user_cnt);
  changeNode("guest-total", guest_cnt);

  /* 종합 - 서비스 수 값 */
  const offi_servi_cnt = stat[stat.length - 1]["official_service_count"];
  const unoffi_servi_cnt = stat[stat.length - 1]["unofficial_service_count"];
  const servi_cnt = offi_servi_cnt + unoffi_servi_cnt;

  changeNode("service-total", servi_cnt);
  changeNode("offi-total", offi_servi_cnt);
  changeNode("unoffi-total", unoffi_servi_cnt);

  /* 종합 - 사용자 수 변동  */
  let user_change = 0;
  let enrol_user_change = 0;
  let grad_user_change = 0;
  let guest_change = 0;

  if (stat.length !== 1) {
    const user_cnt_yest = stat[stat.length - 2]["user_count"];
    const enrol_user_cnt_yest = stat[stat.length - 2]["enrolled_user_count"];
    const grad_user_cnt_yest = stat[stat.length - 2]["graduated_user_count"];
    const guest_cnt_yest =
      user_cnt_yest - (enrol_user_cnt_yest + grad_user_cnt_yest);

    user_change = user_cnt - user_cnt_yest;
    enrol_user_change = enrol_user_cnt - enrol_user_cnt_yest;
    grad_user_change = grad_user_cnt - grad_user_cnt_yest;
    guest_change = guest_cnt - guest_cnt_yest;
  }

  changeNode("user-change", Math.abs(user_change), incrementalTxt(user_change));
  changeNode(
    "enrol-change",
    Math.abs(enrol_user_change),
    incrementalTxt(enrol_user_change)
  );
  changeNode(
    "grad-change",
    Math.abs(grad_user_change),
    incrementalTxt(grad_user_change)
  );
  changeNode(
    "guest-change",
    Math.abs(guest_change),
    incrementalTxt(guest_change)
  );

  /* 종합 - 서비스 수 변동 */
  let servi_change = 0;
  let offi_servi_change = 0;
  let unoffi_servi_change = 0;

  if (stat.length !== 1) {
    const offi_servi_cnt_yest = stat[stat.length - 1]["official_service_count"];
    const unoffi_servi_cnt_yest =
      stat[stat.length - 1]["unofficial_service_count"];
    const servi_cnt_yest = offi_servi_cnt_yest + unoffi_servi_cnt_yest;

    servi_change = servi_cnt - servi_cnt_yest;
    offi_servi_change = offi_servi_cnt - offi_servi_cnt_yest;
    unoffi_servi_change = unoffi_servi_cnt - unoffi_servi_cnt_yest;
  }

  changeNode(
    "service-change",
    Math.abs(servi_change),
    incrementalTxt(servi_change)
  );
  changeNode(
    "offi-change",
    Math.abs(offi_servi_change),
    incrementalTxt(offi_servi_change)
  );
  changeNode(
    "unoffi-change",
    Math.abs(unoffi_servi_change),
    incrementalTxt(unoffi_servi_change)
  );
}
