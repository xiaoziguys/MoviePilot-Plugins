import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "dashboard-widget" };


const _sfc_main = {
  __name: 'Dashboard',
  props: {
  config: {
    default: () => ({})
  },
  allowRefresh: {
    default: true
  }
},
  setup(__props) {

// 仪表板逻辑...

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, null, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, null, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(__props.config.title || '仪表板组件'), 1)
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text)
      ]),
      _: 1
    })
  ]))
}
}

};

export { _sfc_main as default };
