const BundleTracker = require("webpack-bundle-tracker");
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  publicPath: "/vue/",
  pages: {
    base: {
      entry: 'src/base.js',
      chunks: ['chunk-vendors', 'chunk-common']
    },
    builder: {
      entry: 'src/builder.js',
      chunks: ['chunk-vendors', 'chunk-common', 'builder']
    },
    checker: {
      entry: 'src/checker.js',
      chunks: ['chunk-vendors', 'chunk-common', 'checker']
    }
  },
  chainWebpack: config => {
    config
      .plugin('BundleTracker')
      .use(BundleTracker, [{path: '../backend'}])

  },
  transpileDependencies: true
})
