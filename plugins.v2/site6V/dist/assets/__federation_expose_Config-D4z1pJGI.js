import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };

const {ref} = await importShared('vue');


// 接收初始配置和API对象

const _sfc_main = {
  __name: 'Config',
  props: {
  initialConfig: {
    default: () => ({})
  },
  api: {
    default: () => {}
  }
},
  emits: ['save', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

// 配置数据
const config = ref({...props.initialConfig});

// 自定义事件，用于保存配置
const emit = __emit;

// 保存配置
function saveConfig() {
  emit('save', config.value);
}

// 通知主应用切换到详情页面
function notifySwitch() {
  emit('switch');
}

// 通知主应用关闭当前页面
function notifyClose() {
  emit('close');
}

return (_ctx, _cache) => {
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_btn = _resolveComponent("v-btn");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_text_field, {
      modelValue: config.value.someField,
      "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((config.value.someField) = $event)),
      label: "配置项"
    }, null, 8, ["modelValue"]),
    _createVNode(_component_v_btn, {
      color: "primary",
      onClick: saveConfig
    }, {
      default: _withCtx(() => _cache[1] || (_cache[1] = [
        _createTextVNode("保存配置")
      ])),
      _: 1
    }),
    _createVNode(_component_v_btn, {
      color: "primary",
      onClick: notifyClose
    }, {
      default: _withCtx(() => _cache[2] || (_cache[2] = [
        _createTextVNode("关闭页面")
      ])),
      _: 1
    }),
    _createVNode(_component_v_btn, {
      color: "primary",
      onClick: notifySwitch
    }, {
      default: _withCtx(() => _cache[3] || (_cache[3] = [
        _createTextVNode("切换到详情页面")
      ])),
      _: 1
    })
  ]))
}
}

};

export { _sfc_main as default };
