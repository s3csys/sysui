import React, { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Tab,
  Tabs,
  Typography,
} from '@mui/material';
import {
  Add as AddIcon,
  Label as LabelIcon,
  List as ListIcon,
} from '@mui/icons-material';

import ServerList from '../components/servers/ServerList';
import ServerDetail from '../components/servers/ServerDetail';
import ServerForm from '../components/servers/ServerForm';
import ServerTagManager from '../components/servers/ServerTagManager';

const ServersPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<string>('servers');

  // Determine which tab should be active based on the current route
  React.useEffect(() => {
    if (location.pathname.includes('/servers/tags')) {
      setActiveTab('tags');
    } else {
      setActiveTab('servers');
    }
  }, [location.pathname]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: string) => {
    setActiveTab(newValue);
    if (newValue === 'tags') {
      navigate('/servers/tags');
    } else {
      navigate('/servers');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Servers
          </Typography>
          <Box>
            {activeTab === 'servers' && (
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={() => navigate('/servers/add')}
              >
                Add Server
              </Button>
            )}
          </Box>
        </Box>

        <Card>
          <CardContent sx={{ p: 0 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
            >
              <Tab 
                icon={<ListIcon />} 
                iconPosition="start" 
                label="Server List" 
                value="servers" 
              />
              <Tab 
                icon={<LabelIcon />} 
                iconPosition="start" 
                label="Manage Tags" 
                value="tags" 
              />
            </Tabs>
          </CardContent>
        </Card>
      </Box>

      <Routes>
        <Route path="/" element={<ServerList />} />
        <Route path="/add" element={<ServerForm />} />
        <Route path="/:id" element={<ServerDetail />} />
        <Route path="/:id/edit" element={<ServerForm />} />
        <Route path="/tags" element={<ServerTagManager />} />
      </Routes>
    </Container>
  );
};

export default ServersPage;