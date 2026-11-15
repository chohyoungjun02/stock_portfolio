import { defineConfig } from '@apps-in-toss/web-framework/config';

export default defineConfig({
  // 앱인토스 콘솔에 등록한 앱 이름과 같아야 업로드돼요
  appName: 'stockchartstudy',
  permissions: [],  // 카메라·위치 등 기기 권한을 쓰지 않음
  webView: {
    bounces: false,  // 차트를 드래그할 때 화면 전체가 튀지 않도록
  },
  webBundleDir: 'dist',
});
