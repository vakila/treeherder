treeherder.service('ThReactTest', function() {
    this.component = React.createClass({
      render: function() {
        return <div>Hello {this.props.name}</div>;
      }
    });
});
