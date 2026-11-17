export const meta = {
  name: 'wm260-residual-weak-signal-sweep',
  description: 'Investigate the 141 WM260 binaries/libraries left over after the prior strong-signal sweep (weak/ambiguous DUML-adjacent signal, no confirmed relocation), with adversarial reverify on any new command finds',
  phases: [
    { title: 'Investigate', detail: '141 previously-triaged-but-not-escalated binaries' },
    { title: 'Verify', detail: 'adversarial reverify of any genuinely new command candidates' },
  ],
}

const BASE = '/home/user/wm260_fw/decrypted'

const ALL_ITEMS = [
  { key: 'at_gimbalcali.so', paths: [`${BASE}/e1e_extracted/system_files/lib/at_gimbalcali.so`] },
  { key: 'at_v1trigger.so', paths: [`${BASE}/e1e_extracted/system_files/lib/at_v1trigger.so`] },
  { key: 'c2d_ut', paths: [`${BASE}/e1e_extracted/system_files/bin/c2d_ut`, `${BASE}/e2_extracted/system_files/bin/c2d_ut`] },
  { key: 'dds_shell', paths: [`${BASE}/e1e_extracted/system_files/bin/dds_shell`, `${BASE}/e2_extracted/system_files/bin/dds_shell`] },
  { key: 'dds_simulation_test', paths: [`${BASE}/e2_extracted/system_files/bin/dds_simulation_test`] },
  { key: 'dji_dsp_load', paths: [`${BASE}/e1e_extracted/system_files/bin/dji_dsp_load`, `${BASE}/e2_extracted/system_files/bin/dji_dsp_load`] },
  { key: 'dji_media_play_service_test', paths: [`${BASE}/e2_extracted/system_files/bin/dji_media_play_service_test`] },
  { key: 'dsp_frwk_test', paths: [`${BASE}/e2_extracted/system_files/bin/dsp_frwk_test`] },
  { key: 'file_transfer', paths: [`${BASE}/e1e_extracted/system_files/bin/file_transfer`] },
  { key: 'libMediaBase.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libMediaBase.so`] },
  { key: 'libMediaPipeBuilder.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libMediaPipeBuilder.so`] },
  { key: 'libOmxCamCapEngSource.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libOmxCamCapEngSource.so`] },
  { key: 'libOmxCamDispEngSink.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libOmxCamDispEngSink.so`] },
  { key: 'libOmxCore.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libOmxCore.so`, `${BASE}/e2_extracted/system_files/lib64/libOmxCore.so`] },
  { key: 'libOmxDispSink.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libOmxDispSink.so`] },
  { key: 'libOmxDuss.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libOmxDuss.so`, `${BASE}/e2_extracted/system_files/lib64/libOmxDuss.so`] },
  { key: 'libOmxPlayer.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libOmxPlayer.so`, `${BASE}/e2_extracted/system_files/lib64/libOmxPlayer.so`] },
  { key: 'libOmxProresDec.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libOmxProresDec.so`] },
  { key: 'libOmxVC8000DCodec.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libOmxVC8000DCodec.so`] },
  { key: 'libOmxVC8000Enc.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libOmxVC8000Enc.so`] },
  { key: 'libOmxVideoPyramidGen.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libOmxVideoPyramidGen.so`] },
  { key: 'libOmxWlSink.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libOmxWlSink.so`] },
  { key: 'libOmxWlSource.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libOmxWlSource.so`] },
  { key: 'libaudioservice.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libaudioservice.so`] },
  { key: 'libcam_util.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libcam_util.so`, `${BASE}/e2_extracted/system_files/lib64/libcam_util.so`] },
  { key: 'libdcam_2d_hw.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/2d/libdcam_2d_hw.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/2d/libdcam_2d_hw.so`] },
  { key: 'libdcam_audio_frwk.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_audio_frwk.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_audio_frwk.so`] },
  { key: 'libdcam_audiodev.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_audiodev.so`] },
  { key: 'libdcam_blur_stream_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_blur_stream_filter.so`] },
  { key: 'libdcam_camdev.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_camdev.so`] },
  { key: 'libdcam_capture_strategy.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_capture_strategy.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_capture_strategy.so`] },
  { key: 'libdcam_common_filter.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/stream_filter/libdcam_common_filter.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_common_filter.so`] },
  { key: 'libdcam_cp_adj.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/adj/libdcam_cp_adj.so`] },
  { key: 'libdcam_cs_async_resp.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_cs_async_resp.so`] },
  { key: 'libdcam_cs_cbb.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_cs_cbb.so`] },
  { key: 'libdcam_cs_topmode_common_hyperlapse.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/state/libdcam_cs_topmode_common_hyperlapse.so`] },
  { key: 'libdcam_dewarp_gdc.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/dewarp/libdcam_dewarp_gdc.so`] },
  { key: 'libdcam_dewarp_gdc_stitching.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/dewarp/libdcam_dewarp_gdc_stitching.so`] },
  { key: 'libdcam_disp_async.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/disp/libdcam_disp_async.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/disp/libdcam_disp_async.so`] },
  { key: 'libdcam_disp_e1e_lcdc.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/disp/libdcam_disp_e1e_lcdc.so`] },
  { key: 'libdcam_disp_e2_lcdc.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/disp/libdcam_disp_e2_lcdc.so`] },
  { key: 'libdcam_disp_null.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/disp/libdcam_disp_null.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/disp/libdcam_disp_null.so`] },
  { key: 'libdcam_disp_wm260.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/disp/libdcam_disp_wm260.so`] },
  { key: 'libdcam_eis_hw.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/eis/libdcam_eis_hw.so`] },
  { key: 'libdcam_frwk.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_frwk.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_frwk.so`] },
  { key: 'libdcam_gimbal_stabilizes_stream_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_gimbal_stabilizes_stream_filter.so`] },
  { key: 'libdcam_histogram_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_histogram_filter.so`] },
  { key: 'libdcam_hyperlapse_ae_ceva.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/hyperlapse_ae/libdcam_hyperlapse_ae_ceva.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/hyperlapse_ae/libdcam_hyperlapse_ae_ceva.so`] },
  { key: 'libdcam_ienc_hw.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/ienc/libdcam_ienc_hw.so`] },
  { key: 'libdcam_ienc_sw.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/ienc/libdcam_ienc_sw.so`] },
  { key: 'libdcam_iq_module.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_iq_module.so`] },
  { key: 'libdcam_iq_tplgy_util.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_iq_tplgy_util.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_iq_tplgy_util.so`] },
  { key: 'libdcam_lapse_eis.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/lapse_eis/libdcam_lapse_eis.so`] },
  { key: 'libdcam_mctf.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/mctf/libdcam_mctf.so`] },
  { key: 'libdcam_media.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_media.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_media.so`] },
  { key: 'libdcam_meta_convert.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_meta_convert.so`] },
  { key: 'libdcam_muxer.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_muxer.so`] },
  { key: 'libdcam_null_2d.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/2d/libdcam_null_2d.so`] },
  { key: 'libdcam_observer.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_observer.so`] },
  { key: 'libdcam_optical_center_align_stream_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_optical_center_align_stream_filter.so`] },
  { key: 'libdcam_pano_fusion_ceva.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/pano_fusion/libdcam_pano_fusion_ceva.so`] },
  { key: 'libdcam_pano_fusion_eng.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pano_fusion/libdcam_pano_fusion_eng.so`] },
  { key: 'libdcam_pb.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_pb.so`] },
  { key: 'libdcam_pdmonitor.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_pdmonitor.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_pdmonitor.so`] },
  { key: 'libdcam_pp.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_pp.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_pp.so`] },
  { key: 'libdcam_pp_color_fusion.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/yuv_fusion/libdcam_pp_color_fusion.so`] },
  { key: 'libdcam_pp_dgain.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/dgain/libdcam_pp_dgain.so`] },
  { key: 'libdcam_pp_dgain_20.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/dgain/libdcam_pp_dgain_20.so`] },
  { key: 'libdcam_pp_e2_hiso.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_e2_hiso.so`] },
  { key: 'libdcam_pp_gamma.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_gamma.so`] },
  { key: 'libdcam_pp_inter_ma_calc.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_inter_ma_calc.so`] },
  { key: 'libdcam_pp_inter_mee_ebh.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_inter_mee_ebh.so`] },
  { key: 'libdcam_pp_intra_mee_ebh.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_intra_mee_ebh.so`] },
  { key: 'libdcam_pp_llf.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_llf.so`] },
  { key: 'libdcam_pp_llf15.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_llf15.so`] },
  { key: 'libdcam_pp_mee_ebh.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_mee_ebh.so`] },
  { key: 'libdcam_pp_mee_video.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_mee_video.so`] },
  { key: 'libdcam_pp_plant_detect.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_plant_detect.so`] },
  { key: 'libdcam_pp_raw_stack_15.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/raw_stack/libdcam_pp_raw_stack_15.so`] },
  { key: 'libdcam_pp_raw_stack_16.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/raw_stack/libdcam_pp_raw_stack_16.so`] },
  { key: 'libdcam_pp_sisr_strategy.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/pp_algo/libdcam_pp_sisr_strategy.so`] },
  { key: 'libdcam_pp_tino.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/pp_algo/libdcam_pp_tino.so`] },
  { key: 'libdcam_pp_yuv_fusion_16.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/yuv_fusion/libdcam_pp_yuv_fusion_16.so`] },
  { key: 'libdcam_pp_yuv_fusion_17.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/yuv_fusion/libdcam_pp_yuv_fusion_17.so`] },
  { key: 'libdcam_pp_yuv_fusion_20.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/yuv_fusion/libdcam_pp_yuv_fusion_20.so`] },
  { key: 'libdcam_scap1_capeng.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/capture_strategy/libdcam_scap1_capeng.so`] },
  { key: 'libdcam_scap2_capeng.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/capture_strategy/libdcam_scap2_capeng.so`] },
  { key: 'libdcam_scap_fusion_ceva.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/scap_fusion/libdcam_scap_fusion_ceva.so`] },
  { key: 'libdcam_sensor_input_stream_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_sensor_input_stream_filter.so`] },
  { key: 'libdcam_shooter_base_still.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_shooter_base_still.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_shooter_base_still.so`] },
  { key: 'libdcam_shooter_raw_reprocess.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/shooter/libdcam_shooter_raw_reprocess.so`] },
  { key: 'libdcam_shooter_still_common.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/shooter/libdcam_shooter_still_common.so`] },
  { key: 'libdcam_shooter_still_general.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/shooter/libdcam_shooter_still_general.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/shooter/libdcam_shooter_still_general.so`] },
  { key: 'libdcam_shooter_still_yuvraw_zsl.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/shooter/libdcam_shooter_still_yuvraw_zsl.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/shooter/libdcam_shooter_still_yuvraw_zsl.so`] },
  { key: 'libdcam_shooter_video_multi.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/shooter/libdcam_shooter_video_multi.so`] },
  { key: 'libdcam_shooter_video_quick_shot.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/shooter/libdcam_shooter_video_quick_shot.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/shooter/libdcam_shooter_video_quick_shot.so`] },
  { key: 'libdcam_shooter_video_single.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/shooter/libdcam_shooter_video_single.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/shooter/libdcam_shooter_video_single.so`] },
  { key: 'libdcam_sisr_fusion_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_sisr_fusion_filter.so`] },
  { key: 'libdcam_sisr_nn_process_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_sisr_nn_process_filter.so`] },
  { key: 'libdcam_sphere_dewarp_hw.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/sphere_dewarp/libdcam_sphere_dewarp_hw.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/sphere_dewarp/libdcam_sphere_dewarp_hw.so`] },
  { key: 'libdcam_subscribe.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_subscribe.so`] },
  { key: 'libdcam_sw_sync_eis_stream_filter.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/stream_filter/libdcam_sw_sync_eis_stream_filter.so`] },
  { key: 'libdcam_tino_ceva.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/tino/libdcam_tino_ceva.so`] },
  { key: 'libdcam_topmode_comm.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_topmode_comm.so`] },
  { key: 'libdcam_vdaf_mesh_process_link_node.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/link_node/libdcam_vdaf_mesh_process_link_node.so`] },
  { key: 'libdcam_vdec_hw.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/vdec/libdcam_vdec_hw.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/vdec/libdcam_vdec_hw.so`] },
  { key: 'libdcam_venc_h26x.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/venc/libdcam_venc_h26x.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/venc/libdcam_venc_h26x.so`] },
  { key: 'libdcam_video_bps_parser.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_video_bps_parser.so`] },
  { key: 'libdcam_wm260_lcdc_link_node.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/link_node/libdcam_wm260_lcdc_link_node.so`] },
  { key: 'libdcam_wm_multi.so', paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/watermark/libdcam_wm_multi.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/watermark/libdcam_wm_multi.so`] },
  { key: 'libdcam_yuv_fusion_17_stack.so', paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/yuv_fusion/libdcam_yuv_fusion_17_stack.so`] },
  { key: 'libdisplay-server.so', paths: [`${BASE}/e2_extracted/system_files/lib64/libdisplay-server.so`] },
  { key: 'libmediabinder.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libmediabinder.so`] },
  { key: 'libupgrade_module_mngr.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libupgrade_module_mngr.so`, `${BASE}/e2_extracted/system_files/lib64/libupgrade_module_mngr.so`] },
  { key: 'libupgrade_product.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libupgrade_product.so`, `${BASE}/e2_extracted/system_files/lib64/libupgrade_product.so`] },
  { key: 'libupgrade_status_control.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libupgrade_status_control.so`, `${BASE}/e2_extracted/system_files/lib64/libupgrade_status_control.so`] },
  { key: 'libupgrade_status_push.so', paths: [`${BASE}/e1e_extracted/system_files/lib/libupgrade_status_push.so`, `${BASE}/e2_extracted/system_files/lib64/libupgrade_status_push.so`] },
  { key: 'nnf_gtest', paths: [`${BASE}/e2_extracted/system_files/bin/nnf_gtest`] },
  { key: 'omx_camcapeng_source_test', paths: [`${BASE}/e1e_extracted/system_files/bin/omx_camcapeng_source_test`] },
  { key: 'omx_comptest', paths: [`${BASE}/e1e_extracted/system_files/bin/omx_comptest`, `${BASE}/e2_extracted/system_files/bin/omx_comptest`] },
  { key: 'omx_converter_test', paths: [`${BASE}/e2_extracted/system_files/bin/omx_converter_test`] },
  { key: 'omx_coretest', paths: [`${BASE}/e1e_extracted/system_files/bin/omx_coretest`, `${BASE}/e2_extracted/system_files/bin/omx_coretest`] },
  { key: 'omx_playertest', paths: [`${BASE}/e2_extracted/system_files/bin/omx_playertest`] },
  { key: 'omx_sinktest', paths: [`${BASE}/e1e_extracted/system_files/bin/omx_sinktest`] },
  { key: 'omx_wlsinktest', paths: [`${BASE}/e1e_extracted/system_files/bin/omx_wlsinktest`] },
  { key: 'pipe_builder', paths: [`${BASE}/e1e_extracted/system_files/bin/pipe_builder`] },
  { key: 'stress_test_osal_msgq', paths: [`${BASE}/e2_extracted/system_files/bin/stress_test_osal_msgq`] },
  { key: 'testWlSinkUsbBulk', paths: [`${BASE}/e1e_extracted/system_files/bin/testWlSinkUsbBulk`] },
  { key: 'test_c2d', paths: [`${BASE}/e1e_extracted/system_files/bin/test_c2d`] },
  { key: 'test_cam', paths: [`${BASE}/e2_extracted/system_files/bin/test_cam`] },
  { key: 'test_camCapEngSource', paths: [`${BASE}/e1e_extracted/system_files/bin/test_camCapEngSource`] },
  { key: 'test_cpu_loading', paths: [`${BASE}/e2_extracted/system_files/bin/test_cpu_loading`] },
  { key: 'test_disp', paths: [`${BASE}/e1e_extracted/system_files/bin/test_disp`, `${BASE}/e2_extracted/system_files/bin/test_disp`] },
  { key: 'test_dsp2', paths: [`${BASE}/e2_extracted/system_files/bin/test_dsp2`] },
  { key: 'test_flight_lite', paths: [`${BASE}/e1e_extracted/system_files/bin/test_flight_lite`] },
  { key: 'test_imgtec_venc', paths: [`${BASE}/e1e_extracted/system_files/bin/test_imgtec_venc`] },
  { key: 'test_imgtec_venc_new', paths: [`${BASE}/e1e_extracted/system_files/bin/test_imgtec_venc_new`] },
  { key: 'test_rtos_client_publisher', paths: [`${BASE}/e1e_extracted/system_files/bin/test_rtos_client_publisher`] },
  { key: 'test_v2d', paths: [`${BASE}/e1e_extracted/system_files/bin/test_v2d`] },
  { key: 'test_wl_venc', paths: [`${BASE}/e1e_extracted/system_files/bin/test_wl_venc`] },
  { key: 'usb_bulk_xfer_test_v2', paths: [`${BASE}/e2_extracted/system_files/bin/usb_bulk_xfer_test_v2`] },
]

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['summary', 'ruled_out', 'new_command_candidates', 'architecture_findings'],
  properties: {
    summary: { type: 'string' },
    ruled_out: { type: 'boolean', description: 'true if this binary/library confirmed to have zero DUML command-registration role' },
    new_command_candidates: {
      type: 'array',
      items: {
        type: 'object',
        required: ['cmd_set', 'cmd_id', 'proposed_name', 'handler_function', 'already_known', 'evidence', 'confidence'],
        properties: {
          cmd_set: { type: 'string' },
          cmd_id: { type: 'string' },
          proposed_name: { type: 'string' },
          handler_function: { type: 'string' },
          already_known: { type: 'boolean', description: 'true if this (cmd_set,cmd_id) pair is already in ALL_COMMANDS.csv/commands.json' },
          evidence: { type: 'string' },
          confidence: { type: 'string' },
        },
      },
    },
    architecture_findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['summary', 'impact_category', 'confidence', 'evidence'],
        properties: {
          summary: { type: 'string' },
          impact_category: { type: 'string' },
          confidence: { type: 'string' },
          evidence: { type: 'string' },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  required: ['refuted', 'reasoning'],
  properties: {
    refuted: { type: 'boolean' },
    reasoning: { type: 'string' },
  },
}

function investigatePrompt(item) {
  return `You are doing DUML (DJI drone protocol) reverse-engineering research on the public GitHub repo nm844/drone-stuff, working directory /home/user/drone-stuff. This is authorized, defensive vulnerability-research-style documentation work on firmware for a drone the project owner personally owns (DJI Mavic 3 / WM260). The project maintains a machine-readable DUML command registry (currently 898 (cmd_set,cmd_id) pairs) built from duml_py/duml/commands.json, mirrored into DUML_PROTOCOL/ALL_COMMANDS.csv and per-cmd_set DUML_PROTOCOL/cmdset_XX_*.md docs.

FIRST: read /home/user/drone-stuff/DUML_PROTOCOL/ALL_COMMANDS.csv so you know what's already catalogued, to avoid reporting known commands as new.

YOUR TARGET: "${item.key}", at these exact file path(s) (ARM32 e1e_extracted and/or aarch64 e2_extracted builds — a binary present on both architectures implements the same logic, so treat them as one investigation, cross-checking between them only if one architecture's build is clearer than the other):
${item.paths.map(p => `  - ${p}`).join('\n')}

CONTEXT ON WHY THIS TARGET IS HERE: this binary/library was flagged by an earlier mechanical triage pass across all 808 binaries in both firmware images as carrying some DUML-adjacent string or symbol signal (e.g. a duss_*/duml_* symbol reference, or a string like "duml"/"mb_"/"route"), but NOT as having a confirmed direct ELF relocation into one of the three known DUML command-registration entry points (see below) — that stronger-signal set was already fully investigated in a prior round (see DUML_PROTOCOL/16_EXHAUSTIVE_SWEEP_FINDINGS.md for that round's results and house style). This is therefore the weaker-signal residual: a plausible true-negative (e.g. a library that merely LINKS a framework which itself touches DUML elsewhere, without this specific binary doing any registration) is a perfectly legitimate and expected outcome for many targets in this batch — do not strain to manufacture a positive finding. But you must reach that conclusion by actually checking, not by assuming the weak-signal label was correct: this project's own history includes a case where the INITIAL mechanical relocation scan used "readelf -r" (narrow output), which silently truncates symbol names on 32-bit ARM binaries and produced false negatives until someone switched to "readelf -rW" (wide). Always use -rW (or -W generally) on any 32-bit ARM binary relocation/symbol dump in this investigation, and treat the fact that this target lacked strong signal in the ORIGINAL triage as a hint, not a verified conclusion.

THREE KNOWN DUML COMMAND-REGISTRATION MECHANISMS in this firmware's binaries — check for all three using real tools (readelf -rW, readelf -sW, objdump -d, capstone/pyelftools if useful), not surface-level string greps alone:
1. Direct calls to the imported function duss_event_register_dynamic_command(cmd_set, cmd_id, handler_fn, ...) — cmd_set/cmd_id loaded as literal immediates into registers (ARM32: r0-r3; aarch64: x0-x3) immediately before the bl/blx call site.
2. The duss_mb_create_route_table + duss_event_create_client client/route idiom (a named route/client registration, not necessarily a per-(cmd_set,cmd_id) one — see DUML_PROTOCOL/16_EXHAUSTIVE_SWEEP_FINDINGS.md's app_echo writeup for a worked example of how to tell whether this idiom registers specific commands or not).
3. An R_ARM_RELATIVE/R_AARCH64_RELATIVE-relocated .data array of 8-byte {function_pointer, cmd_word} rows (cmd_word low byte = cmd_set, high byte = cmd_id) — the dji_flight vaddr 0xae0f8 precedent. Be careful to distinguish a genuine command-dispatch table from a compiler-generated C++/unwinder function-pointer table (same shape, unrelated purpose) — check where the resolved pointers actually point.

Many binaries in this batch are camera-pipeline plugin libraries (libdcam_*.so) loaded by a camera-framework host process, OMX media-codec libraries, upgrade-subsystem helper libraries, or small test/diagnostic CLIs. For a plugin library, check whether it implements the registration calls ITSELF (unlikely but check) versus merely exporting plugin entry points that a host process calls into (in which case this specific library has no DUML role of its own — note that finding and move on; do not re-investigate the host process, which is out of scope here). For test/diagnostic CLIs, apply the same app_echo-style scrutiny: does it establish its own route/client with a real dynamically-assigned route id, or does it just link the framework without calling these APIs at all?

HARD BOUNDARIES (non-negotiable, verbatim project-wide rules):
- NEVER open, disassemble, or discuss command IDs for libamt_util.so (OP-TEE TA UUID e91c9402-64a0-470f-88e7-bf5d3c606b6a) — not part of this task, skip entirely even if imported.
- Document architecture, commands, and security weaknesses in vulnerability-research style (name the weakness, impact category, confidence) — NEVER produce working exploit payloads, crafted attack packets, forged authorization/activation tokens, cryptanalysis of live security mechanisms, or step-by-step attack recipes. Stick to describing what you found and why it matters, not how to abuse it.
- Do not conflate duss_event's private internal bus-event-type numbering with the wire-level DUML cmd_set/cmd_id space — these are different namespaces; only report a new_command_candidate when you have genuine evidence of a wire-level DUML (cmd_set,cmd_id) registration, not just any numeric tag that happens to look like one.

Return via the required schema: a summary of what you found, whether this target is ruled_out (true = confirmed zero DUML command-registration role), any new_command_candidates (only ones with real evidence, cross-checked against ALL_COMMANDS.csv yourself — set already_known accurately), and any architecture_findings worth recording (informational observations, access-control gaps, insecure IPC patterns, etc. — same vocabulary as DUML_PROTOCOL/16_EXHAUSTIVE_SWEEP_FINDINGS.md) even if ruled_out is true, since a real negative with an interesting architectural detail is still worth noting. If this is a totally uninteresting library with nothing beyond "links framework X, no DUML role, no notable findings," it's fine to say exactly that briefly — don't manufacture content.`
}

function verifyPrompt(candidate) {
  return `Adversarially verify this claimed NEW DUML command finding from WM260 firmware reverse-engineering research (repo nm844/drone-stuff, working dir /home/user/drone-stuff). Your job is to try to REFUTE it — default to refuted=true if you cannot independently confirm it.

Claimed finding:
  cmd_set: ${candidate.cmd_set}
  cmd_id: ${candidate.cmd_id}
  proposed_name: ${candidate.proposed_name}
  handler_function: ${candidate.handler_function}
  claimed already_known: ${candidate.already_known}
  evidence given: ${candidate.evidence}
  confidence given: ${candidate.confidence}
  source binary/paths: ${JSON.stringify(candidate._paths)}

Steps:
1. Check /home/user/drone-stuff/DUML_PROTOCOL/ALL_COMMANDS.csv and duml_py/duml/commands.json yourself — if this (cmd_set,cmd_id) pair is ALREADY in there, this is not a new finding; refute it (even if the pair is "real", it brings nothing new to catalogue).
2. Independently re-derive the registration evidence from the raw binary at the given path(s) yourself — re-run readelf -rW / readelf -sW / objdump -d / a disassembler on the actual file, do not just trust the prose description. Confirm the cmd_set/cmd_id values really are loaded as literal immediates (or really are present in a genuine relocated command-dispatch array, not a compiler-generated unwinder table) at the claimed call/table site.
3. Confirm the handler function is a real, distinct function in this binary (not a trampoline/PLT stub pointing elsewhere, not a misread address).
4. Confirm this isn't a duss_event private bus-event-type number being mistaken for a wire-level DUML cmd_set/cmd_id.

Return refuted=true unless you can affirmatively confirm all of the above from the raw binary yourself. Give brief reasoning either way.`
}

phase('Investigate')

const investigated = await pipeline(
  ALL_ITEMS,
  item => agent(investigatePrompt(item), { label: `investigate:${item.key}`, phase: 'Investigate', schema: FINDINGS_SCHEMA })
    .then(r => r ? { ...r, _key: item.key, _paths: item.paths } : null)
)

const validInvestigations = investigated.filter(Boolean)
log(`Investigated ${validInvestigations.length}/${ALL_ITEMS.length} targets.`)

const allCandidates = validInvestigations.flatMap(inv =>
  (inv.new_command_candidates || [])
    .filter(c => c.already_known === false)
    .map(c => ({ ...c, _source_key: inv._key, _paths: inv._paths }))
)

log(`${allCandidates.length} candidate new command(s) found across all targets; adversarially reverifying each.`)

phase('Verify')

const verified = await pipeline(
  allCandidates,
  async (candidate) => {
    const votes = await parallel([1, 2, 3].map(() => () =>
      agent(verifyPrompt(candidate), { label: `verify:${candidate._source_key}:${candidate.cmd_set}/${candidate.cmd_id}`, phase: 'Verify', schema: VERDICT_SCHEMA })
    ))
    const validVotes = votes.filter(Boolean)
    const refuteCount = validVotes.filter(v => v.refuted).length
    const survives = validVotes.length > 0 && refuteCount < Math.ceil(validVotes.length / 2)
    return { candidate, votes: validVotes, survives }
  }
)

const candidateNewCommandsVerified = verified
  .filter(v => v && v.survives)
  .map(v => v.candidate)

return {
  investigations: validInvestigations,
  all_candidates_considered: allCandidates,
  candidate_new_commands_verified: candidateNewCommandsVerified,
  verify_detail: verified,
  stats: {
    total_targets: ALL_ITEMS.length,
    investigated: validInvestigations.length,
    ruled_out: validInvestigations.filter(i => i.ruled_out).length,
    not_ruled_out: validInvestigations.filter(i => !i.ruled_out).length,
    candidates_found: allCandidates.length,
    candidates_verified: candidateNewCommandsVerified.length,
  },
}
