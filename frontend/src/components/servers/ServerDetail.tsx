import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Paper,
  Stack,
  Typography,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  CheckCircle as OnlineIcon,
  Cancel as OfflineIcon,
  ArrowBack as BackIcon,
} from '@mui/icons-material';
import serverService, { ServerDetail as ServerDetailType } from '../../services/serverService';

const ServerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [server, setServer] = useState<ServerDetailType | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const fetchServerDetail = async () => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await serverService.getServer(parseInt(id, 10));
      setServer(data);
    } catch (err) {
      console.error('Error fetching server details:', err);
      setError('Failed to load server details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServerDetail();
  }, [id]);

  const handleRefreshStatus = async () => {
    if (!id) return;
    
    setRefreshing(true);
    try {
      const updatedServer = await serverService.checkServerStatus(parseInt(id, 10));
      setServer(updatedServer);
    } catch (err) {
      console.error('Error refreshing server status:', err);
      setError('Failed to refresh server status. Please try again.');
    } finally {
      setRefreshing(false);
    }
  };

  const handleDeleteServer = async () => {
    if (!id) return;
    
    if (window.confirm('Are you sure you want to delete this server?')) {
      try {
        await serverService.deleteServer(parseInt(id, 10));
        navigate('/servers');
      } catch (err) {
        console.error('Error deleting server:', err);
        setError('Failed to delete server. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
        <Button color="inherit" size="small" onClick={fetchServerDetail} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  if (!server) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Server not found
        <Button component={Link} to="/servers" color="inherit" size="small" sx={{ ml: 2 }}>
          Back to Servers
        </Button>
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Button
            component={Link}
            to="/servers"
            startIcon={<BackIcon />}
            sx={{ mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h5" component="h1">
            {server.name}
          </Typography>
          {server.status && (
            <Chip
              icon={
                server.status.is_online ? (
                  <OnlineIcon fontSize="small" />
                ) : (
                  <OfflineIcon fontSize="small" />
                )
              }
              label={server.status.is_online ? 'Online' : 'Offline'}
              color={server.status.is_online ? 'success' : 'error'}
              size="small"
            />
          )}
        </Stack>
        <Stack direction="row" spacing={1}>
          <Button
            onClick={handleRefreshStatus}
            startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
            disabled={refreshing}
          >
            Refresh Status
          </Button>
          <Button
            component={Link}
            to={`/servers/${id}/edit`}
            startIcon={<EditIcon />}
            variant="outlined"
          >
            Edit
          </Button>
          <Button
            onClick={handleDeleteServer}
            startIcon={<DeleteIcon />}
            variant="outlined"
            color="error"
          >
            Delete
          </Button>
        </Stack>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Server Information" />
            <Divider />
            <CardContent>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    IP Address
                  </Typography>
                  <Typography variant="body1">{server.ip_address}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    SSH Port
                  </Typography>
                  <Typography variant="body1">{server.ssh_port}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Description
                  </Typography>
                  <Typography variant="body1">
                    {server.description || 'No description provided'}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Status
                  </Typography>
                  <Box display="flex" alignItems="center" mt={0.5}>
                    {server.status ? (
                      <>
                        {server.status.is_online ? (
                          <>
                            <OnlineIcon color="success" />
                            <Typography variant="body1" sx={{ ml: 1 }}>
                              Online
                            </Typography>
                          </>
                        ) : (
                          <>
                            <OfflineIcon color="error" />
                            <Typography variant="body1" sx={{ ml: 1 }}>
                              Offline
                              {server.status.error_message && (
                                <Typography variant="body2" color="error">
                                  {server.status.error_message}
                                </Typography>
                              )}
                            </Typography>
                          </>
                        )}
                      </>
                    ) : (
                      'Unknown'
                    )}
                  </Box>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Tags
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {server.tags.length > 0 ? (
                      server.tags.map((tag) => (
                        <Chip key={tag.id} label={tag.name} size="small" />
                      ))
                    ) : (
                      <Typography variant="body2" color="textSecondary">
                        No tags
                      </Typography>
                    )}
                  </Box>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Created At
                  </Typography>
                  <Typography variant="body1">
                    {new Date(server.created_at).toLocaleString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Updated At
                  </Typography>
                  <Typography variant="body1">
                    {new Date(server.updated_at).toLocaleString()}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Connection Information" />
            <Divider />
            <CardContent>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Username
                  </Typography>
                  <Typography variant="body1">{server.credentials.username}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Authentication Type
                  </Typography>
                  <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                    {server.credentials.auth_type}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Password/Key
                  </Typography>
                  <Typography variant="body1">
                    {server.credentials.auth_type === 'password' ? '********' : 'SSH Key (hidden)'}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          {server.system_info && (
            <Card sx={{ mt: 3 }}>
              <CardHeader title="System Information" />
              <Divider />
              <CardContent>
                <Stack spacing={2}>
                  {Object.entries(server.system_info).map(([key, value]) => (
                    <Box key={key}>
                      <Typography variant="subtitle2" color="textSecondary">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      </Typography>
                      <Typography variant="body1">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ServerDetail;