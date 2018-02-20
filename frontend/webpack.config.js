var path = require('path');
var webpack = require('webpack');

module.exports = {
  devtool: 'eval',
  entry: [
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/only-dev-server',
    './src/boot'
  ],
  output: {
    path: path.join(__dirname, 'dist'),
    filename: 'bundle.js',
    publicPath: '/static/'
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin()
  ],
  module: {
    loaders: [
    {
      test: /\.js$/,
      exclude: /node_modules/,
      loaders: ['react-hot', 'babel?presets[]=es2015,presets[]=stage-0,presets[]=react'],
      include: path.join(__dirname, 'src')
    }

    ]
  },
  node: {
    fs: 'empty',
    child_process: 'empty'
  }
};
