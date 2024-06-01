const path = require('path');

module.exports = {
    entry: './static/src/js/index.js',
    output: {
        path: path.resolve(__dirname, 'static/dist'),
        filename: 'bundle.js',
    },
    mode: 'development',

    watch: true,

    module: {
        rules: [
            {
                test: /\.css$/i,
                include: path.resolve(__dirname, 'static/src/css'),
                use: [ 'style-loader', 'css-loader', 'postcss-loader' ],
            },
        ],
    },
};

