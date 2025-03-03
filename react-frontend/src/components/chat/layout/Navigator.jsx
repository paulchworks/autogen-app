import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';

const item = {
  py: '2px',
  px: 3,
  color: 'rgba(255, 255, 255, 0.7)',
  '&:hover, &:focus': {
    bgcolor: 'rgba(255, 255, 255, 0.08)',
  },
};

const itemCategory = {
  boxShadow: '0 -1px 0 rgb(255,255,255,0.1) inset',
  py: 1.5,
  px: 3,
};

export default function Navigator(props) {
    const { ...other } = props;
    return (
        <Drawer variant="permanent" {...other}>
            <List disablePadding>
                <ListItem sx={{ ...item, ...itemCategory, fontSize: 16, color: '#ffg' }}>
                <h1>PaulchWorks Consultant</h1>
                </ListItem>
                <ListItem sx={{ ...item, ...itemCategory, fontSize: 12, color: '#ffg' }}>
                <p>This is a sample chat application built with Autogen and Azure AI Search</p>
                </ListItem>
            </List>
        </Drawer>
    );
}